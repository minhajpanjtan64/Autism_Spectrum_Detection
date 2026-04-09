from __future__ import annotations

from pathlib import Path

import firebase_admin
from firebase_admin import auth, credentials

from backend.core.config import get_settings


class FirebaseConfigError(RuntimeError):
    pass


def _initialize_firebase_if_needed() -> None:
    if firebase_admin._apps:
        return

    settings = get_settings()
    cred_path = settings.firebase_credentials_path

    if cred_path:
        path = Path(cred_path)
        if not path.exists():
            raise FirebaseConfigError(f"Firebase credentials file not found at: {cred_path}")
        firebase_admin.initialize_app(credentials.Certificate(str(path)))
        return

    try:
        firebase_admin.initialize_app()
    except Exception as exc:
        raise FirebaseConfigError(
            "Firebase is not configured. Set FIREBASE_CREDENTIALS_PATH in .env or configure default credentials."
        ) from exc


def verify_id_token(id_token: str) -> dict:
    _initialize_firebase_if_needed()
    return auth.verify_id_token(id_token)
