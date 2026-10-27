"""Shared fixtures for the `db`-marked integration suite (migrations, auth).
Nothing here runs for the default `pytest` pass — every fixture that needs
Postgres/Redis is only pulled in by a test that already depends on
`clean_db`, so the fast suite stays infra-free."""

import pytest
import sqlalchemy as sa
from alembic.config import Config

from alembic import command
from app.core.config import settings
from app.core.redis import redis_client

SYNC_DATABASE_URL = settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")


def _alembic_config() -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)
    return cfg


@pytest.fixture
def db_schema():
    """Ensures the schema is at `head` before a test runs. Deliberately not
    session-scoped with a single teardown: `test_migrations.py`'s own tests
    independently upgrade/downgrade the same database, and pytest gives no
    guarantee about file execution order — a session fixture that upgrades
    once and assumes that holds for every later test would break the first
    time collection order put a migrations test in between. An upgrade on
    an already-head database is a fast no-op, so doing this per-test costs
    nothing worth avoiding."""
    command.upgrade(_alembic_config(), "head")
    yield


@pytest.fixture
def clean_db(db_schema):
    """Empties every app table between tests, so unique constraints
    (`device_id`, `phone_number`, ...) never collide across test cases."""
    engine = sa.create_engine(SYNC_DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(
            sa.text(
                "TRUNCATE TABLE orders.order_items, orders.favorites, orders.orders, "
                "catalog.menu_items, catalog.promo_codes, catalog.restaurants, iam.users "
                "RESTART IDENTITY CASCADE"
            )
        )
        conn.commit()
    yield
    engine.dispose()


@pytest.fixture
async def clean_redis(clean_db):
    """Pairs with `clean_db`: most DB-backed tests also touch Redis (rate
    limiting), so they'd otherwise carry state between cases too."""
    await redis_client.flushdb()
    yield
    await redis_client.flushdb()
