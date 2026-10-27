"""Async engine/session factory — the runtime counterpart to `app/db/base.py`
(which Alembic uses for migrations, not live request handling)."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    # asyncpg caches a prepared statement's column/enum type OIDs per
    # connection. If a migration (Alembic, possibly a rolling deploy with
    # the old process still serving) drops and recreates a type — e.g. a
    # Postgres ENUM, which gets a new OID each time even with the same
    # name — any connection whose cache predates that change starts
    # raising "cache lookup failed for type NNNNN" on every query that
    # touches it, not just the first one after the change. Disabling the
    # statement cache trades a little per-query overhead for not having a
    # whole connection silently wedged until the pool recycles it.
    connect_args={"statement_cache_size": 0},
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
