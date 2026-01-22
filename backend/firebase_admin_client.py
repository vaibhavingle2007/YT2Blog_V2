import json
from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import credentials, auth, firestore

from backend.config import settings


_app: Optional[firebase_admin.App] = None
_db: Optional[firestore.Client] = None


def init_firebase() -> None:
    """
    Initialize Firebase Admin SDK exactly once.
    Supports either FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH.
    """
    global _app, _db
    if _app is not None:
        return

    if not settings.has_firebase_admin:
        raise RuntimeError(
            "Firebase Admin is not configured. Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH."
        )

    cred_obj: credentials.Base = None  # type: ignore[assignment]
    if settings.FIREBASE_SERVICE_ACCOUNT_JSON and settings.FIREBASE_SERVICE_ACCOUNT_JSON.strip():
        try:
            payload: Dict[str, Any] = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
        except json.JSONDecodeError as e:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not valid JSON") from e
        cred_obj = credentials.Certificate(payload)
    else:
        cred_obj = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)

    _app = firebase_admin.initialize_app(cred_obj, {"projectId": settings.FIREBASE_PROJECT_ID})
    _db = firestore.client(_app)


def get_db() -> firestore.Client:
    init_firebase()
    assert _db is not None
    return _db


def verify_id_token(id_token: str) -> Dict[str, Any]:
    init_firebase()
    return auth.verify_id_token(id_token)

