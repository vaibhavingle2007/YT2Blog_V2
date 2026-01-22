from typing import Optional, Dict, Any

from fastapi import Header, HTTPException

from backend.firebase_admin_client import verify_id_token


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    scheme, token = parts[0], parts[1]
    if scheme.lower() != "bearer":
        return None
    return token.strip() or None


async def require_firebase_user(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """
    FastAPI dependency that validates Firebase ID token from:
      Authorization: Bearer <FirebaseIdToken>
    Returns decoded token dict with `uid` as the canonical user id.
    """
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing Authorization Bearer token")
    try:
        decoded = verify_id_token(token)
        if "uid" not in decoded:
            raise HTTPException(status_code=401, detail="Invalid token (missing uid)")
        return decoded
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")

