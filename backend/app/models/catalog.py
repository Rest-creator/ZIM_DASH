"""`catalog` schema — public reference data (database_design.md Section 2.2-2.4).

`restaurants.service_zone`/`.location` (ADR-008 geospatial columns, plus the
`postgis` extension itself) are deliberately NOT here yet — they arrive with
ZD-M1-10, per the migration sequencing in database_design.md Section 5.
"""

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = {"schema": "catalog"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    cuisine: Mapped[str | None] = mapped_column(sa.String(64))
    rating: Mapped[float | None] = mapped_column(sa.Numeric(2, 1))
    delivery_fee_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    # Static string, per PRD Section 3 — a dynamic ETA is Phase 3.
    delivery_time_range: Mapped[str | None] = mapped_column(sa.String(32))
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(sa.Text))
    brand_color: Mapped[str | None] = mapped_column(sa.String(7))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.true())
    is_accepting_orders: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.true()
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        sa.Index("idx_menu_items_restaurant", "restaurant_id"),
        {"schema": "catalog"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("catalog.restaurants.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    price_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    category: Mapped[str | None] = mapped_column(sa.String(64))
    is_popular: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.false())


class DiscountType(str, enum.Enum):
    PERCENT = "PERCENT"
    FLAT = "FLAT"


class PromoCode(Base):
    __tablename__ = "promo_codes"
    __table_args__ = {"schema": "catalog"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(sa.String(32), unique=True, nullable=False)
    discount_type: Mapped[DiscountType] = mapped_column(
        PgEnum(
            DiscountType,
            name="discount_type",
            schema="catalog",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    discount_value: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    minimum_subtotal_cents: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="0"
    )
