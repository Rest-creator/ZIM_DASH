from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

# Populates Base.metadata with every table (see app/models/__init__.py) —
# autogenerate reads Base.metadata, not this import, but nothing is on it
# until the models are imported somewhere.
import app.models  # noqa: E402,F401
from alembic import context
from app.core.config import settings
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Alembic runs synchronously; the app's own DATABASE_URL uses the async
# asyncpg driver, so swap it for the sync psycopg one here rather than
# keeping a second URL to drift out of sync with the first.
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://"),
)

# The schemas this app actually owns and migrates — none of our tables ever
# live in `public`. Without this filter, autogenerate also reflects the
# postgis_tiger_geocoder extension's hundreds of tables (installed straight
# into `public` by the postgis/postgis image) and proposes dropping all of
# them on every run, since they're not in our SQLAlchemy metadata either.
MANAGED_SCHEMAS = {"iam", "catalog", "orders", "ledger"}


def include_name(name: str | None, type_: str, parent_names: dict) -> bool:
    if type_ == "schema":
        return name in MANAGED_SCHEMAS
    if type_ == "table":
        return parent_names.get("schema_name") in MANAGED_SCHEMAS
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Every table lives in iam/catalog/orders, never public — without
        # this, autogenerate silently ignores all of them.
        include_schemas=True,
        include_name=include_name,
        version_table_schema="public",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            version_table_schema="public",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
