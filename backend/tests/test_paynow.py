"""Unit tests for Paynow hash verification — no DB/Redis needed.

`SAMPLE_MESSAGE`/`SAMPLE_HASH`/`SAMPLE_KEY` are copied verbatim from
Paynow's own published worked example
(developers.paynow.co.zw/docs/validating_hash.html), not invented — this is
what proves `verify_and_parse` implements their actual documented algorithm,
not just a plausible-looking guess at it.
"""

import pytest

from app.core.paynow import PaynowHashError, _parse_raw, verify_and_parse

SAMPLE_KEY = "3e9fed89-60e1-4ce5-ab6e-6b1eb2d4f977"
SAMPLE_MESSAGE = (
    "status=Ok&browserurl=https%3a%2f%2fstaging.paynow.co.zw%2fPayment%2fConfirmPayment%2f9510"
    "&pollurl=https%3a%2f%2fstaging.paynow.co.zw%2fInterface%2fCheckPayment%2f%3fguid%3dc7ed41da"
    "-0159-46da-b428-69549f770413&paynowreference=9510"
    "&hash=750DD0B0DF374678707BB5AF915AF81C228B9058AD57BB7120569EC68BBB9C2E"
    "FC1B26C6375D2BC562AC909B3CD6B2AF1D42E1A5E479FFAC8F4FB3FDCE71DF4D"
)


def test_the_documented_sample_message_verifies():
    # This sample has no `reference`/`status` (lowercase)/`amount` field —
    # it's the hash-algorithm worked example, not a real status update — so
    # assert on the hash-dependent fields it does have via a raw parse,
    # rather than through the full PaynowStatusUpdate shape (see the
    # "real-shaped" tests below for that).
    fields = _parse_raw(SAMPLE_MESSAGE.encode("utf-8"), SAMPLE_KEY)
    assert fields["paynowreference"] == "9510"


def test_a_tampered_message_is_rejected():
    tampered = SAMPLE_MESSAGE.replace("paynowreference=9510", "paynowreference=9999")
    with pytest.raises(PaynowHashError, match="Hash does not match"):
        verify_and_parse(tampered.encode("utf-8"), SAMPLE_KEY)


def test_the_wrong_integration_key_is_rejected():
    with pytest.raises(PaynowHashError, match="Hash does not match"):
        verify_and_parse(SAMPLE_MESSAGE.encode("utf-8"), "a-different-key")


def _signed_message(key: str, **fields: str) -> bytes:
    """Builds a status-update message and signs it ourselves — for the
    fields a real status update actually carries (`reference`, `status`,
    `amount`, ...), which the documented hash-algorithm sample above
    doesn't, so these round-trip through our own signer instead of a
    second copy-pasted vector."""
    import urllib.parse
    from hashlib import sha512

    query = "&".join(f"{k}={urllib.parse.quote_plus(v)}" for k, v in fields.items())
    digest = (
        sha512("".join(fields.values()).encode("utf-8") + key.encode("utf-8")).hexdigest().upper()
    )
    return f"{query}&hash={digest}".encode()


def test_a_well_formed_status_update_parses():
    message = _signed_message(
        SAMPLE_KEY,
        reference="order-123",
        paynowreference="9999",
        amount="25.00",
        status="Paid",
        pollurl="https://paynow.co.zw/poll/abc",
    )
    update = verify_and_parse(message, SAMPLE_KEY)
    assert update.reference == "order-123"
    assert update.status_lower == "paid"


def test_a_message_missing_a_required_field_is_rejected():
    import urllib.parse
    from hashlib import sha512

    fields = {"reference": "order-1", "status": "Paid"}  # no amount/paynowreference/pollurl
    query = "&".join(f"{k}={urllib.parse.quote_plus(v)}" for k, v in fields.items())
    digest = (
        sha512("".join(fields.values()).encode("utf-8") + SAMPLE_KEY.encode("utf-8"))
        .hexdigest()
        .upper()
    )
    message = f"{query}&hash={digest}".encode()

    with pytest.raises(PaynowHashError, match="missing required field"):
        verify_and_parse(message, SAMPLE_KEY)
