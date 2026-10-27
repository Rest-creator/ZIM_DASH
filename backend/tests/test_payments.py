"""Integration tests for the `/payments/paynow/webhook` endpoint, against
real Postgres (and a mocked poll-back, so these don't need network access
to Paynow's actual servers)."""

import urllib.parse
import uuid
from hashlib import sha512
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.models.catalog import Restaurant
from app.models.iam import IdentityType, User
from app.models.orders import Order

pytestmark = pytest.mark.db


async def _client() -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


def _sign(**fields: str) -> bytes:
    query = "&".join(f"{k}={urllib.parse.quote_plus(v)}" for k, v in fields.items())
    digest = (
        sha512(
            "".join(fields.values()).encode("utf-8")
            + settings.paynow_integration_key.encode("utf-8")
        )
        .hexdigest()
        .upper()
    )
    return f"{query}&hash={digest}".encode()


async def _create_order(payment_reference: str) -> uuid.UUID:
    async with SessionLocal() as session:
        user = User(identity_type=IdentityType.ANONYMOUS, device_id=f"device-{payment_reference}")
        restaurant = Restaurant(name="Test Diner", delivery_fee_cents=100)
        session.add_all([user, restaurant])
        await session.flush()

        order = Order(
            customer_id=user.id,
            restaurant_id=restaurant.id,
            currency="USD",
            subtotal_cents=1000,
            delivery_fee_cents=100,
            service_fee_cents=50,
            total_cents=1150,
            payment_method="ECOCASH",
            payment_reference=payment_reference,
            customer_name="Test Customer",
            customer_phone="+263771111111",
            destination_suburb="Avondale",
        )
        session.add(order)
        await session.commit()
        return order.id


async def test_a_paid_status_marks_the_order_paid(clean_db):
    order_id = await _create_order("ref-paid-1")
    message = _sign(
        reference="ref-paid-1",
        paynowreference="9001",
        amount="11.50",
        status="Paid",
        pollurl="https://paynow.co.zw/poll/9001",
    )

    with patch(
        "app.api.payments.confirm_via_poll", new=AsyncMock(return_value=_poll_result("Paid"))
    ):
        async with await _client() as client:
            response = await client.post(
                "/payments/paynow/webhook",
                content=message,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    assert response.status_code == 200
    async with SessionLocal() as session:
        order = await session.get(Order, order_id)
        assert order.payment_status == "PAID"


async def test_an_invalid_hash_is_rejected_without_touching_the_order(clean_db):
    order_id = await _create_order("ref-bad-hash")
    message = _sign(
        reference="ref-bad-hash",
        paynowreference="9002",
        amount="11.50",
        status="Paid",
        pollurl="https://paynow.co.zw/poll/9002",
    ).replace(b"Paid", b"Evil")

    async with await _client() as client:
        response = await client.post(
            "/payments/paynow/webhook",
            content=message,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    assert response.status_code == 400
    async with SessionLocal() as session:
        order = await session.get(Order, order_id)
        assert order.payment_status == "PENDING"


async def test_a_poll_confirmation_mismatch_does_not_update_the_order(clean_db):
    """The pushed message says Paid, but polling Paynow back says
    Cancelled — the polled status is the one that's trusted."""
    order_id = await _create_order("ref-poll-mismatch")
    message = _sign(
        reference="ref-poll-mismatch",
        paynowreference="9003",
        amount="11.50",
        status="Paid",
        pollurl="https://paynow.co.zw/poll/9003",
    )

    with patch(
        "app.api.payments.confirm_via_poll", new=AsyncMock(return_value=_poll_result("Cancelled"))
    ):
        async with await _client() as client:
            response = await client.post(
                "/payments/paynow/webhook",
                content=message,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    assert response.status_code == 200
    async with SessionLocal() as session:
        order = await session.get(Order, order_id)
        assert order.payment_status == "CANCELLED"


async def test_an_unknown_reference_is_acknowledged_without_error(clean_db):
    message = _sign(
        reference="no-such-order",
        paynowreference="9004",
        amount="11.50",
        status="Paid",
        pollurl="https://paynow.co.zw/poll/9004",
    )

    with patch(
        "app.api.payments.confirm_via_poll", new=AsyncMock(return_value=_poll_result("Paid"))
    ):
        async with await _client() as client:
            response = await client.post(
                "/payments/paynow/webhook",
                content=message,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    assert response.status_code == 200


def _poll_result(status_value: str):
    from app.core.paynow import PaynowStatusUpdate

    return PaynowStatusUpdate(
        reference="irrelevant-for-the-test",
        paynow_reference="irrelevant",
        amount="11.50",
        status=status_value,
        poll_url="https://paynow.co.zw/poll/irrelevant",
    )
