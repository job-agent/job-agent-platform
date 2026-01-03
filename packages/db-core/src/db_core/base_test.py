"""Tests for declarative Base.

Note: Tests for import paths and module exports have been removed
as they test implementation details rather than observable behavior.
The remaining tests verify actual functionality that affects runtime behavior.
"""

from sqlalchemy import Column, Integer, String

from db_core.base import Base


class TestBaseDeclarativeMapping:
    """Test suite for declarative Base functionality."""

    def test_base_can_define_model_with_table(self):
        """Base can be used to define model classes with table mapping."""

        class TestModel(Base):
            __tablename__ = "test_table_for_mapping"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        # Verify the model is properly registered and usable
        assert "test_table_for_mapping" in Base.metadata.tables
        assert TestModel.__tablename__ == "test_table_for_mapping"

    def test_model_columns_are_mapped_correctly(self):
        """Model columns defined via Base are properly mapped."""

        class ColumnTestModel(Base):
            __tablename__ = "column_test_table"
            id = Column(Integer, primary_key=True)
            value = Column(String(100))

        table = Base.metadata.tables["column_test_table"]
        column_names = [c.name for c in table.columns]
        assert "id" in column_names
        assert "value" in column_names
