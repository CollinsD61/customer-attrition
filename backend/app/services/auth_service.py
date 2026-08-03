from datetime import UTC, datetime, timedelta

import jwt

from backend.app.core.config import settings

ALGORITHM = "HS256"


def create_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(hours=24)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
