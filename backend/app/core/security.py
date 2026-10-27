"""Password hashing and JWT issuance/decoding.

Plain `bcrypt` rather than `passlib[bcrypt]` — passlib's bcrypt backend has
had ongoing compatibility breaks against bcrypt>=4.1 and the project is
effectively unmaintained; calling bcrypt directly is one less moving part.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings
from app.models.iam import IdentityType


class TokenError(Exception):
    """A JWT that doesn't verify, has expired, or is missing the claims a
    valid ZIM DASH token must carry."""


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: uuid.UUID, identity_type: IdentityType) -> str:
    """`sub` is the `iam.users.id` this token authenticates — per
    database_design.md Section 2.1, the same id for a user's whole
    lifetime, anonymous or named."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "identity_type": identity_type.value,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> tuple[uuid.UUID, IdentityType]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc

    try:
        user_id = uuid.UUID(payload["sub"])
        identity_type = IdentityType(payload["identity_type"])
    except (KeyError, ValueError) as exc:
        raise TokenError("Token is missing a required claim") from exc

    return user_id, identity_type
