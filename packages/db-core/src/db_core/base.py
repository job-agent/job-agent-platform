"""SQLAlchemy declarative base for models.

This module provides the declarative Base class for defining SQLAlchemy models.
Consumer packages can either use this shared Base or define their own for
Alembic migration isolation.
"""

from sqlalchemy.orm import declarative_base


Base = declarative_base()
