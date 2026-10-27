"""Importing this package populates Base.metadata with every table — the
thing Alembic's autogenerate (and `Base.metadata.create_all` in tests)
actually reads. A model defined but never imported here is invisible to
both."""

from app.models import catalog, iam, orders  # noqa: F401
