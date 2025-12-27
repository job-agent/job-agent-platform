"""Tests for declarative Base export."""

from db_core.base import Base


class TestBase:
    """Test suite for declarative Base."""

    def test_base_is_exported(self):
        """Base is exported from db_core.base."""
        assert Base is not None

    def test_base_has_metadata(self):
        """Base has metadata attribute for table definitions."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

    def test_base_can_be_used_as_declarative_base(self):
        """Base can be used to define model classes."""
        from sqlalchemy import Column, Integer, String

        # Define a test model using the Base
        class TestModel(Base):
            __tablename__ = "test_table"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        # Verify the model is properly registered
        assert "test_table" in Base.metadata.tables
        assert TestModel.__tablename__ == "test_table"

    def test_base_metadata_tracks_tables(self):
        """Base.metadata tracks all defined tables."""
        from sqlalchemy import Column, Integer, String

        initial_table_count = len(Base.metadata.tables)

        class AnotherTestModel(Base):
            __tablename__ = "another_test_table"
            id = Column(Integer, primary_key=True)
            value = Column(String(100))

        assert len(Base.metadata.tables) == initial_table_count + 1
        assert "another_test_table" in Base.metadata.tables

    def test_base_has_registry(self):
        """Base has registry for mapper configuration."""
        # SQLAlchemy 2.0 uses registry
        assert hasattr(Base, "registry")


class TestBaseImportability:
    """Test that Base can be imported from various locations."""

    def test_import_from_base_module(self):
        """Base can be imported from db_core.base."""
        from db_core.base import Base as BaseFromModule

        assert BaseFromModule is not None

    def test_import_from_package(self):
        """Base can be imported from db_core package root."""
        from db_core import Base as BaseFromPackage

        assert BaseFromPackage is not None

    def test_both_imports_return_same_base(self):
        """Importing Base from different locations returns the same object."""
        from db_core.base import Base as BaseFromModule
        from db_core import Base as BaseFromPackage

        assert BaseFromModule is BaseFromPackage
