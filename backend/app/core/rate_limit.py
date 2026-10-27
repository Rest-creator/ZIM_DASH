"""A minimal fixed-window rate limiter, Redis-backed so it works correctly
across multiple API processes (an in-memory counter would reset per worker
and defeat the point).

threat_model.md Section 3/4: `/auth/anonymous` must be rate-limited so an
attacker can't mint unlimited device identities to place fraudulent orders
or abuse promo codes. Order-creation and promo-redemption endpoints need
the same treatment once they exist (ZD-M1-05 / Epic 1) — this dependency
is written to be reused there, not auth-specific.
"""

from fastapi import HTTPException, Request, status

from app.core.redis import redis_client


def rate_limit(key_prefix: str, limit: int, window_seconds: int):
    """A FastAPI dependency factory: `limit` requests per `window_seconds`,
    per source IP, under `key_prefix`.

    Keyed on `request.client.host` — correct only if the ASGI server itself
    sees the real client IP. Behind a reverse proxy (Caddy/nginx), that
    means trusting `X-Forwarded-For` there, not in this dependency; no
    proxy is configured yet, so this is accurate for now and worth
    revisiting when one is.
    """

    async def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{key_prefix}:{client_ip}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, window_seconds)
        if count > limit:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests. Try again later.",
            )

    return dependency
