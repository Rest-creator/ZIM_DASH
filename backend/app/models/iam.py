"""`iam` schema — identity (database_design.md Section 2.1).

One row per identity, anonymous or named: `/auth/anonymous` (ZD-M1-03)
creates a row here, and `/auth/register` (Epic 4) upgrades the *same* row in
place (sets phone_number/password_hash, flips identity_type to NAMED)
rather than migrating foreign keys to a new one.
"""

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, Index, text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IdentityType(str, enum.Enum):
    ANONYMOUS = "ANONYMOUS"
    NAMED = "NAMED"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "identity_type = 'ANONYMOUS' OR phone_number IS NOT NULL",
            name="named_requires_phone",
        ),
        Index(
            "idx_users_device_id",
            "device_id",
            unique=True,
            postgresql_where=text("device_id IS NOT NULL"),
        ),
        {"schema": "iam"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    identity_type: Mapped[IdentityType] = mapped_column(
        PgEnum(
            IdentityType,
            name="identity_type",
            schema="iam",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        server_default=IdentityType.ANONYMOUS.value,
    )
    # Set for ANONYMOUS identities (ADR-003).
    device_id: Mapped[str | None] = mapped_column(sa.String(128))
    # Set on upgrade to NAMED (Epic 4).
    phone_number: Mapped[str | None] = mapped_column(sa.String(20), unique=True)
    password_hash: Mapped[str | None] = mapped_column(sa.String(255))
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.false())
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
