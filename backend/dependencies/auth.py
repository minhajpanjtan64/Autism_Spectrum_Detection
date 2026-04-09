from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.config import get_settings
from backend.core.firebase import FirebaseConfigError, verify_id_token

security = HTTPBearer(auto_error=False)


@dataclass
class AuthUser:
    uid: str
    email: str | None = None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthUser:
    settings = get_settings()

    if not settings.firebase_auth_required:
        return AuthUser(uid="dev-user", email=None)

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header.",
        )

    try:
        decoded = verify_id_token(credentials.credentials)
    except FirebaseConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token.",
        ) from exc

    uid = decoded.get("uid")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing uid.",
        )

    return AuthUser(uid=uid, email=decoded.get("email"))


def resolve_user_id(request_user_id: str | None, auth_user: AuthUser) -> str:
    if request_user_id and request_user_id != auth_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request user_id does not match authenticated user.",
        )
    return auth_user.uid
