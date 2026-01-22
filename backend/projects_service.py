from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.firebase_admin_client import get_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_project(uid: str, project: Dict[str, Any]) -> str:
    db = get_db()
    ref = db.collection("users").document(uid).collection("projects").document()
    payload = dict(project)
    payload["created_at"] = payload.get("created_at") or _now_iso()
    payload["updated_at"] = _now_iso()
    payload["user_id"] = uid
    ref.set(payload, merge=True)
    return ref.id


def list_projects(uid: str, limit: int = 20) -> List[Dict[str, Any]]:
    db = get_db()
    q = (
        db.collection("users")
        .document(uid)
        .collection("projects")
        .order_by("created_at", direction="DESCENDING")
        .limit(limit)
    )
    results: List[Dict[str, Any]] = []
    for doc in q.stream():
        data = doc.to_dict() or {}
        data["id"] = doc.id
        results.append(data)
    return results

