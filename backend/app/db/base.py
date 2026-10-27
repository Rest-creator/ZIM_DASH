"""The declarative base every ORM model inherits from.

A fixed naming convention (rather than SQLAlchemy/Postgres defaults) so
Alembic's autogenerate produces stable, readable constraint names instead of
opaque auto-numbered ones (`orders_customer_id_fkey` vs `fk_something_1234`).
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
