"""Request/response shapes for the `/auth/*` endpoints.

No documented phone-number format or password policy exists yet (checked
SRS/PRD) — `PHONE_PATTERN` and the 8-character password minimum are
reasonable placeholders, not a decided policy; revisit if/when one lands.
"""

import re
import uuid

from pydantic import BaseModel, Field, field_validator

from app.models.iam import IdentityType

PHONE_PATTERN = re.compile(r"^\+?[0-9]{9,15}$")


def _validate_phone(value: str) -> str:
    if not PHONE_PATTERN.match(value):
        raise ValueError("phone_number must be 9-15 digits, optionally starting with '+'")
    return value


class AnonymousAuthRequest(BaseModel):
    # Client-generated and persisted locally (ADR-003/ADR-004) so the same
    # device always maps back to the same iam.users row, instead of a new
    # one every time its token expires.
    device_id: str = Field(min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    phone_number: str
    password: str = Field(min_length=8, max_length=72)  # bcrypt's own input limit is 72 bytes

    _validate_phone_number = field_validator("phone_number")(_validate_phone)


class LoginRequest(BaseModel):
    phone_number: str
    password: str

    _validate_phone_number = field_validator("phone_number")(_validate_phone)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    identity_type: IdentityType


class CurrentUser(BaseModel):
    id: uuid.UUID
    identity_type: IdentityType
    device_id: str | None
    phone_number: str | None
    is_verified: bool
