from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

import stripe

from backend.config import settings
from backend.firebase_admin_client import get_db


@dataclass(frozen=True)
class Plan:
    id: str
    daily_credits: int
    is_premium: bool
    stripe_price_id: Optional[str]


PLANS: Dict[str, Plan] = {
    "free": Plan(id="free", daily_credits=5, is_premium=False, stripe_price_id=None),
    "starter": Plan(id="starter", daily_credits=50, is_premium=True, stripe_price_id=settings.STRIPE_PRICE_STARTER),
    "pro": Plan(id="pro", daily_credits=200, is_premium=True, stripe_price_id=settings.STRIPE_PRICE_PRO),
}


def _user_ref(uid: str):
    return get_db().collection("users").document(uid)


def ensure_stripe() -> None:
    if not settings.has_stripe:
        raise RuntimeError("Stripe not configured. Set STRIPE_SECRET_KEY.")
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(uid: str, plan_id: str) -> str:
    if plan_id not in PLANS or plan_id == "free":
        raise ValueError("INVALID_PLAN")
    plan = PLANS[plan_id]

    # If Stripe is not configured (college/demo scenario), directly apply the plan for free.
    if not settings.has_stripe or not plan.stripe_price_id:
        _apply_plan(uid, plan_id)
        return None

    ensure_stripe()

    # Store selected plan so webhook can apply it.
    _user_ref(uid).set({"pending_plan_id": plan_id}, merge=True)

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.PUBLIC_APP_URL}/pricing?success=1",
        cancel_url=f"{settings.PUBLIC_APP_URL}/pricing?canceled=1",
        client_reference_id=uid,
        metadata={"uid": uid, "plan_id": plan_id},
    )
    return session.url


def _apply_plan(uid: str, plan_id: str) -> None:
    plan = PLANS.get(plan_id) or PLANS["free"]
    _user_ref(uid).set(
        {
            "plan_id": plan.id,
            "is_premium": plan.is_premium,
            "credits_total": plan.daily_credits,
            # top up remaining to at least plan daily credits
            "credits_remaining": plan.daily_credits,
            "pending_plan_id": None,
        },
        merge=True,
    )


def handle_webhook(payload: bytes, sig_header: str) -> Dict[str, Any]:
    ensure_stripe()
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("Stripe webhook secret missing. Set STRIPE_WEBHOOK_SECRET.")

    event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=settings.STRIPE_WEBHOOK_SECRET)

    # Apply plan on successful checkout completion.
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        uid = (session.get("metadata") or {}).get("uid") or session.get("client_reference_id")
        plan_id = (session.get("metadata") or {}).get("plan_id")
        if uid and plan_id:
            _apply_plan(uid, plan_id)

    return {"received": True, "type": event["type"]}

