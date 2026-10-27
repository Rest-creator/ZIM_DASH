"""The JWT middleware tasks.md asks for: a dependency every protected route
takes, which resolves the caller's `iam.users` row from their bearer token
or refuses the request. Shared by `/auth/me` now and every `orders`/
`order_items`/`favorites` endpoint later (threat_model.md's row-level
isolation requirement depends on every such route actually using this,
not rolling its own check)."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenError, decode_access_token
from app.db.session import get_db
from app.models.iam import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        user_id, _identity_type = decode_access_token(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await db.get(User, user_id)
    if user is None:
        # The token verifies fine but its subject is gone (e.g. a deleted
        # account) — same response as a bad token, not a 404: nothing
        # about *why* authentication failed should be more specific than
        # that to an unauthenticated caller.
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def find_by_device_id(db: AsyncSession, device_id: str) -> User | None:
    result = await db.execute(select(User).where(User.device_id == device_id))
    return result.scalar_one_or_none()


async def find_by_phone_number(db: AsyncSession, phone_number: str) -> User | None:
    result = await db.execute(select(User).where(User.phone_number == phone_number))
    return result.scalar_one_or_none()
