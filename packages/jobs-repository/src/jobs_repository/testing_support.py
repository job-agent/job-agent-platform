"""Testing utilities for jobs repository."""

import json
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import String, TypeDecorator

from jobs_repository.database.base import Base


class JSONArray(TypeDecorator):
    """Custom type that stores arrays as JSON in SQLite."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value: Any, dialect: Any):
        if value is not None:
            return json.loads(value)
        return value


class SqliteTestDatabase:
    """SQLite-backed test database for repository operations."""

    def __init__(self) -> None:
        self._engine = self._create_engine()
        self._session_factory = sessionmaker(bind=self._engine)

    @staticmethod
    def _create_engine() -> Engine:
        engine = create_engine(
            "sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}
        )
        for table in Base.metadata.tables.values():
            table.schema = None
            for column in table.columns:
                if column.type.__class__.__name__ == "ARRAY":
                    column.type = JSONArray()
        Base.metadata.create_all(engine)
        return engine

    def create_session(self):
        return self._session_factory()

    def dispose(self) -> None:
        self._engine.dispose()
