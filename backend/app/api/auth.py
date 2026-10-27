"""`/auth/*` — ZD-M1-03.

`/auth/anonymous` issues a device-scoped token with no login screen
(ADR-003's whole point); `/auth/register` upgrades that SAME `iam.users`
row to a named account in place, never creating a second row
(database_design.md Section 2.1 — this is what keeps Epic 4 Task 4.3,
migrating order history on upgrade, a no-op); `/auth/login` authenticates
an existing named account; `/auth/me` is the first route built on the JWT
middleware (`get_current_user`), proving it actually protects something.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import find_by_device_id, find_by_phone_number, get_current_user
from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.iam import IdentityType, User
from app.schemas.auth import (
    AnonymousAuthRequest,
    AuthResponse,
    CurrentUser,
    LoginRequest,
    RegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_anonymous_rate_limit = rate_limit(
    "auth_anonymous",
    settings.anonymous_auth_rate_limit,
    settings.anonymous_auth_rate_limit_window_seconds,
)


@router.post(
    "/anonymous",
    response_model=AuthResponse,
    dependencies=[Depends(_anonymous_rate_limit)],
)
async def auth_anonymous(
    body: AnonymousAuthRequest, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    user = await find_by_device_id(db, body.device_id)
    if user is None:
        user = User(identity_type=IdentityType.ANONYMOUS, device_id=body.device_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    # A device that has since registered keeps its NAMED identity here —
    # the token reflects whatever the row currently is, never forces a
    # downgrade back to ANONYMOUS.
    token = create_access_token(user.id, user.identity_type)
    return AuthResponse(access_token=token, user_id=user.id, identity_type=user.identity_type)


@router.post("/register", response_model=AuthResponse)
async def auth_register(
    body: RegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    if current_user.identity_type == IdentityType.NAMED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This account is already registered")

    existing = await find_by_phone_number(db, body.phone_number)
    if existing is not None and existing.id != current_user.id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Phone number already registered")

    current_user.phone_number = body.phone_number
    current_user.password_hash = hash_password(body.password)
    current_user.identity_type = IdentityType.NAMED
    await db.commit()
    await db.refresh(current_user)

    token = create_access_token(current_user.id, current_user.identity_type)
    return AuthResponse(
        access_token=token, user_id=current_user.id, identity_type=current_user.identity_type
    )


@router.post("/login", response_model=AuthResponse)
async def auth_login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    user = await find_by_phone_number(db, body.phone_number)
    # Same error either way — confirming "that phone number isn't
    # registered" to an unauthenticated caller is its own information leak.
    invalid = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid phone number or password")
    if user is None or user.identity_type != IdentityType.NAMED or user.password_hash is None:
        raise invalid
    if not verify_password(body.password, user.password_hash):
        raise invalid

    token = create_access_token(user.id, user.identity_type)
    return AuthResponse(access_token=token, user_id=user.id, identity_type=user.identity_type)


@router.get("/me", response_model=CurrentUser)
async def auth_me(current_user: User = Depends(get_current_user)) -> CurrentUser:
    return CurrentUser(
        id=current_user.id,
        identity_type=current_user.identity_type,
        device_id=current_user.device_id,
        phone_number=current_user.phone_number,
        is_verified=current_user.is_verified,
    )
