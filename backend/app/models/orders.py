"""`orders` schema — order lifecycle (database_design.md Section 2.5-2.7).

`destination_location` (ADR-008) arrives with ZD-M1-10 once `postgis` is
enabled; `destination_plus_code`/`destination_landmark`/
`destination_instructions` (ADR-011) arrive with ZD-M1-15 — both per the
migration sequencing in database_design.md Section 5. `destination_suburb`
is NOT deferred and is included here.
"""

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"  # created, awaiting payment
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"  # ZD-M1-04 webhook verified
    RESTAURANT_ACCEPTED = "RESTAURANT_ACCEPTED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    COURIER_ASSIGNED = "COURIER_ASSIGNED"  # Epic 2 (blocked on Risk R-2)
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("currency IN ('USD', 'ZWG')", name="currency_allowed"),
        CheckConstraint(
            "payment_method IN ('ECOCASH', 'CARD', 'CASH')", name="payment_method_allowed"
        ),
        Index("idx_orders_customer", "customer_id"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_created_at", "created_at"),
        {"schema": "orders"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    # Optimistic-concurrency control (database_design.md Section 2.5): a
    # status update is conditioned on this matching the value the caller
    # last read; zero rows updated means a concurrent write won, and the API
    # returns 409 rather than silently clobbering it.
    version: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="1")
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("catalog.restaurants.id"), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        PgEnum(
            OrderStatus,
            name="order_status",
            schema="orders",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        server_default=OrderStatus.PENDING.value,
    )
    # Locked at checkout (ADR-010) — never recomputed from a live rate after.
    currency: Mapped[str] = mapped_column(sa.String(3), nullable=False)
    subtotal_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    delivery_fee_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    service_fee_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    tip_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    discount_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    total_cents: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    payment_method: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    payment_status: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default="PENDING"
    )
    payment_reference: Mapped[str | None] = mapped_column(sa.String(128), unique=True)
    customer_name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    customer_phone: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    destination_suburb: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )


class OrderItem(Base):
    """Snapshotted at purchase time, so a later menu edit never rewrites
    order history."""

    __tablename__ = "order_items"
    __table_args__ = (
        Index("idx_order_items_order", "order_id"),
        {"schema": "orders"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.orders.id"), nullable=False
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("catalog.menu_items.id"), nullable=False
    )
    name_snapshot: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    price_cents_snapshot: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="1")
    notes: Mapped[str | None] = mapped_column(sa.Text)


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "restaurant_id", name="uq_favorites_user_restaurant"),
        {"schema": "orders"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("catalog.restaurants.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
