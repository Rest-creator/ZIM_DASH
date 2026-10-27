"""Application settings, read from the environment (or `.env` locally).

Only the connection strings the Docker Compose stack (ZD-M1-02) actually
stands up — Postgres and Redis — live here so far. Auth secrets, Paynow
keys, and anything else land in this file as the tasks that need them
(ZD-M1-01, 03, 04, ...) are built, not ahead of time.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ZIM DASH API"
    environment: str = "local"

    database_url: str = "postgresql+asyncpg://zimdash:zimdash@localhost:5432/zimdash"
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
