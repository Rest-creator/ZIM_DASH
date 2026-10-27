"""Integration test for the ZD-M1-01 migration — exercises Alembic itself
(not just `Base.metadata.create_all`), against a real Postgres.

Needs `DATABASE_URL` pointing at a live database (e.g. `docker compose up -d
db` from the repo root, then `.env`'s default of localhost:5432 applies).
Not run as part of the default unit-test pass; see backend/README.md.
"""

import pytest
import sqlalchemy as sa
from alembic.config import Config

from alembic import command
from app.core.config import settings

pytestmark = pytest.mark.db


def _alembic_config() -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option(
        "sqlalchemy.url",
        settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://"),
    )
    return cfg


@pytest.fixture
def migrated_db():
    cfg = _alembic_config()
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


def test_migration_creates_the_expected_tables(migrated_db):
    engine = sa.create_engine(
        settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    )
    with engine.connect() as conn:
        rows = conn.execute(
            sa.text(
                "SELECT table_schema, table_name FROM information_schema.tables "
                "WHERE table_schema IN ('iam', 'catalog', 'orders') "
                "ORDER BY table_schema, table_name"
            )
        ).all()

    assert rows == [
        ("catalog", "menu_items"),
        ("catalog", "promo_codes"),
        ("catalog", "restaurants"),
        ("iam", "users"),
        ("orders", "favorites"),
        ("orders", "order_items"),
        ("orders", "orders"),
    ]


def test_named_user_without_a_phone_number_is_rejected(migrated_db):
    engine = sa.create_engine(
        settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    )
    with (
        engine.connect() as conn,
        pytest.raises(sa.exc.IntegrityError, match="named_requires_phone"),
    ):
        conn.execute(sa.text("INSERT INTO iam.users (identity_type) VALUES ('NAMED')"))
        conn.commit()


def test_downgrade_leaves_no_schemas_or_types_behind(migrated_db):
    engine = sa.create_engine(
        settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    )
    command.downgrade(_alembic_config(), "base")

    with engine.connect() as conn:
        schemas = conn.execute(
            sa.text(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name IN ('iam', 'catalog', 'orders')"
            )
        ).all()
        types = conn.execute(
            sa.text(
                "SELECT typname FROM pg_type WHERE typname IN "
                "('identity_type', 'discount_type', 'order_status')"
            )
        ).all()

    assert schemas == []
    assert types == []

    # Re-upgrade so the `migrated_db` fixture's own teardown (another
    # downgrade) has something to act on rather than erroring on a
    # not-at-head database.
    command.upgrade(_alembic_config(), "head")
