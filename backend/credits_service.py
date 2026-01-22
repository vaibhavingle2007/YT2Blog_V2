from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any

from firebase_admin import firestore as fb_firestore

from backend.firebase_admin_client import get_db


# For the college/demo project, give plenty of free credits so no payment is needed.
FREE_DAILY_CREDITS = 100


@dataclass(frozen=True)
class CreditsSnapshot:
    credits_remaining: int
    credits_total: int
    is_premium: bool
    plan_id: str
    updated_at: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _user_doc(uid: str) -> fb_firestore.DocumentReference:
    db = get_db()
    return db.collection("users").document(uid)


def ensure_user_exists(uid: str, email: str | None = None) -> None:
    ref = _user_doc(uid)
    snap = ref.get()
    if snap.exists:
        # opportunistically store email if missing
        if email:
            data = snap.to_dict() or {}
            if not data.get("email"):
                ref.set({"email": email, "updated_at": _now_iso()}, merge=True)
        return

    ref.set(
        {
            "uid": uid,
            "email": email,
            "plan_id": "free",
            "is_premium": False,
            "credits_remaining": FREE_DAILY_CREDITS,
            "credits_total": FREE_DAILY_CREDITS,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        },
        merge=True,
    )


def get_credits(uid: str) -> CreditsSnapshot:
    ref = _user_doc(uid)
    snap = ref.get()
    if not snap.exists:
        ensure_user_exists(uid)
        snap = ref.get()

    data: Dict[str, Any] = snap.to_dict() or {}
    return CreditsSnapshot(
        credits_remaining=int(data.get("credits_remaining", FREE_DAILY_CREDITS)),
        credits_total=int(data.get("credits_total", FREE_DAILY_CREDITS)),
        is_premium=bool(data.get("is_premium", False)),
        plan_id=str(data.get("plan_id", "free")),
        updated_at=str(data.get("updated_at", _now_iso())),
    )


def consume_credits(uid: str, amount: int = 1) -> CreditsSnapshot:
    if amount <= 0:
        return get_credits(uid)

    db = get_db()
    ref = _user_doc(uid)

    @fb_firestore.transactional
    def _txn(txn: fb_firestore.Transaction) -> Dict[str, Any]:
        snap = ref.get(transaction=txn)
        if not snap.exists:
            txn.set(
                ref,
                {
                    "uid": uid,
                    "plan_id": "free",
                    "is_premium": False,
                    "credits_remaining": FREE_DAILY_CREDITS,
                    "credits_total": FREE_DAILY_CREDITS,
                    "created_at": _now_iso(),
                    "updated_at": _now_iso(),
                },
                merge=True,
            )
            snap = ref.get(transaction=txn)

        data: Dict[str, Any] = snap.to_dict() or {}
        remaining = int(data.get("credits_remaining", FREE_DAILY_CREDITS))
        total = int(data.get("credits_total", FREE_DAILY_CREDITS))
        is_premium = bool(data.get("is_premium", False))
        plan_id = str(data.get("plan_id", "free"))

        if remaining < amount:
            raise ValueError("INSUFFICIENT_CREDITS")

        remaining -= amount
        txn.update(ref, {"credits_remaining": remaining, "updated_at": _now_iso()})
        return {
            "credits_remaining": remaining,
            "credits_total": total,
            "is_premium": is_premium,
            "plan_id": plan_id,
            "updated_at": _now_iso(),
        }

    txn = db.transaction()
    result = _txn(txn)
    return CreditsSnapshot(
        credits_remaining=int(result["credits_remaining"]),
        credits_total=int(result["credits_total"]),
        is_premium=bool(result["is_premium"]),
        plan_id=str(result["plan_id"]),
        updated_at=str(result["updated_at"]),
    )

