"""Paynow status-update verification and poll-back (ZD-M1-04).

Algorithm confirmed against Paynow's own published worked example
(developers.paynow.co.zw/docs/validating_hash.html, sample integration key
`3e9fed89-60e1-4ce5-ab6e-6b1eb2d4f977`) — this implementation's output was
checked byte-for-byte against that page's sample message and expected hash
before being trusted, not inferred from a spec description alone.

Field names and status values per
developers.paynow.co.zw/docs/status_update.html.
"""

import urllib.parse
from dataclasses import dataclass
from hashlib import sha512

import httpx

from app.core.config import settings

# Paid successfully; funds held in suspense until the merchant confirms
# delivery, or already released ("Paid"). All three count as "money has
# actually moved" per status_update.html — "Delivered" additionally means
# delivery was acknowledged and funds clear after a 24h window, but the
# payment itself already succeeded to reach that state.
PAID_STATUSES = {"paid", "awaiting delivery", "delivered"}
CANCELLED_STATUSES = {"cancelled"}
REFUNDED_STATUSES = {"refunded"}


class PaynowHashError(Exception):
    """A status-update message whose `hash` field doesn't verify."""


@dataclass
class PaynowStatusUpdate:
    reference: str
    paynow_reference: str
    amount: str
    status: str
    poll_url: str

    @property
    def status_lower(self) -> str:
        return self.status.strip().lower()


def _parse_raw(raw_body: bytes, integration_key: str) -> dict[str, str]:
    """Parses a raw `application/x-www-form-urlencoded` status-update body
    and verifies its `hash`, exactly per Paynow's documented algorithm:
    split on `&`/first `=`, URL-decode every value except `hash`, join with
    no separator, append the integration key, SHA512, uppercase hex.
    Returns every other field, lowercased, raising `PaynowHashError` if the
    hash doesn't match.

    Deliberately parses the raw bytes rather than going through FastAPI's
    `Form(...)` dependency: Starlette would URL-decode the values once
    already, and re-applying `unquote` here on top of that would corrupt
    any value containing a literal `%` — reading the wire bytes ourselves
    keeps "decode exactly once, per the spec" unambiguous.
    """
    message = raw_body.decode("utf-8")
    fields: dict[str, str] = {}
    hash_value: str | None = None
    ordered_values: list[str] = []

    for pair in message.split("&"):
        if not pair:
            continue
        key, _, value = pair.partition("=")
        decoded = urllib.parse.unquote_plus(value)
        if key.lower() == "hash":
            hash_value = decoded
        else:
            fields[key.lower()] = decoded
            ordered_values.append(decoded)

    if hash_value is None:
        raise PaynowHashError("Message has no hash field")

    computed = (
        sha512("".join(ordered_values).encode("utf-8") + integration_key.encode("utf-8"))
        .hexdigest()
        .upper()
    )
    if computed != hash_value.upper():
        raise PaynowHashError("Hash does not match")

    return fields


def verify_and_parse(
    raw_body: bytes, integration_key: str = settings.paynow_integration_key
) -> PaynowStatusUpdate:
    """`_parse_raw` plus shaping into the fields a real status update
    carries (status_update.html's "core fields") — separate from hash
    verification itself, since Paynow's own worked hash example doesn't
    carry all of them (it demonstrates the algorithm, not a real update)."""
    fields = _parse_raw(raw_body, integration_key)
    try:
        return PaynowStatusUpdate(
            reference=fields["reference"],
            paynow_reference=fields["paynowreference"],
            amount=fields["amount"],
            status=fields["status"],
            poll_url=fields["pollurl"],
        )
    except KeyError as exc:
        raise PaynowHashError(f"Message is missing required field {exc}") from exc


async def confirm_via_poll(poll_url: str) -> PaynowStatusUpdate:
    """Paynow's own guidance (status_update.html): for an update that
    matters (a payment having been made), re-confirm by polling the
    transaction's `pollurl` server-to-server rather than trusting the
    pushed message alone — the same hash verification applies to the
    poll response.

    An empty POST, per the docs ("send an empty HTTP POST to the
    pollurl").
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(poll_url)
        response.raise_for_status()
    return verify_and_parse(response.content)
