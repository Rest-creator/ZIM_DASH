"""`/payments/paynow/*` — ZD-M1-04.

A status update is only ever trusted after its hash verifies (ADR-005/
threat_model.md: payment verification happens server-side, never inferred
from the client). For an update that reports money actually moved, Paynow's
own guidance (status_update.html) is to also poll the transaction's
`pollurl` before acting — this handler does both before writing
`payment_status`, not either in isolation.

Deliberately out of scope here (left to their own tasks): `orders.status`
(the order lifecycle state machine, ZD-M1-05) and the ledger posting
(ZD-M1-14, which itself depends on this task plus ZD-M1-13's ledger
schema) — this endpoint only ever writes `orders.orders.payment_status`.
"""

import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.paynow import (
    CANCELLED_STATUSES,
    PAID_STATUSES,
    REFUNDED_STATUSES,
    PaynowHashError,
    confirm_via_poll,
    verify_and_parse,
)
from app.db.session import get_db
from app.models.orders import Order

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments/paynow", tags=["payments"])


@router.post("/webhook")
async def paynow_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> PlainTextResponse:
    raw_body = await request.body()

    try:
        update = verify_and_parse(raw_body)
    except PaynowHashError as exc:
        logger.warning("paynow_webhook_hash_rejected", extra={"reason": str(exc)})
        return PlainTextResponse("invalid hash", status_code=status.HTTP_400_BAD_REQUEST)

    trusted_status = update.status_lower
    if trusted_status in PAID_STATUSES | CANCELLED_STATUSES | REFUNDED_STATUSES:
        # Paynow's own recommendation for an update that matters: confirm
        # by polling, not by trusting the pushed message alone, however
        # well it hashed.
        try:
            confirmed = await confirm_via_poll(update.poll_url)
        except Exception as exc:
            # Poll-transport failures and PaynowHashError both land here
            # deliberately: either way, we cannot trust this update yet,
            # and a webhook handler should never 500 on an external call
            # failing.
            logger.warning(
                "paynow_webhook_poll_confirmation_failed",
                extra={"reference": update.reference, "reason": str(exc)},
            )
            # Acknowledge receipt regardless — Paynow's retry behaviour on
            # a non-2xx isn't documented, and a transient poll failure on
            # our/their end isn't something re-delivering the same push
            # fixes. The payment_status is simply not updated this round;
            # a later push (status polling, or Paynow's own retry) gets
            # another chance to confirm it.
            return PlainTextResponse("ok")
        trusted_status = confirmed.status_lower

    result = await db.execute(select(Order).where(Order.payment_reference == update.reference))
    order = result.scalar_one_or_none()
    if order is None:
        logger.warning("paynow_webhook_unknown_reference", extra={"reference": update.reference})
        return PlainTextResponse("ok")

    if trusted_status in PAID_STATUSES:
        order.payment_status = "PAID"
    elif trusted_status in CANCELLED_STATUSES:
        order.payment_status = "CANCELLED"
    elif trusted_status in REFUNDED_STATUSES:
        order.payment_status = "REFUNDED"
    else:
        # Created/Sent/Disputed/anything else: not yet a payment-status
        # change this endpoint is responsible for (Disputed in particular
        # is a ledger/ops concern, not a bare column flip).
        logger.info(
            "paynow_webhook_status_noted",
            extra={"reference": update.reference, "status": update.status},
        )
        return PlainTextResponse("ok")

    await db.commit()
    return PlainTextResponse("ok")
