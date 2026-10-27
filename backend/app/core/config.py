"""Application settings, read from the environment (or `.env` locally).

Paynow keys and anything else land in this file as the tasks that need
them (ZD-M1-04, ...) are built, not ahead of time.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ZIM DASH API"
    environment: str = "local"

    database_url: str = "postgresql+asyncpg://zimdash:zimdash@localhost:5432/zimdash"
    redis_url: str = "redis://localhost:6379/0"

    # Dev-only fallback — every non-local environment MUST override this.
    # There is no key-rotation story yet (a rotated key invalidates every
    # outstanding token at once, named and anonymous); noted as a follow-up
    # for whichever task first needs it.
    jwt_secret_key: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    # No refresh-token flow exists yet (ZD-M1-03 scope is auth issuance, not
    # rotation), so this is also each token's total lifetime. 30 days,
    # matching ADR-003's low-friction goal — forcing a customer to re-auth
    # often defeats "no login screen required to place an order." The
    # threat model accepts a stolen token's blast radius as "theft only
    # exposes one user's session" (threat_model.md Section 3); it does not
    # yet weigh that against a 30-day window specifically.
    jwt_access_token_expire_minutes: int = 60 * 24 * 30

    # /auth/anonymous rate limit (threat_model.md Section 3: "An attacker
    # requests unlimited anonymous JWTs ... to place fraudulent orders or
    # abuse promo codes" — flagged there as "Open — not yet implemented,
    # ZD-M1-03"). Per source IP, since there is no identity yet to key on.
    # A starting value, not a tuned one — revisit with real traffic.
    anonymous_auth_rate_limit: int = 5
    anonymous_auth_rate_limit_window_seconds: int = 60


settings = Settings()
