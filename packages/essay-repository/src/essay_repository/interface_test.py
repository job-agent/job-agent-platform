"""Tests for IEssayRepository interface definition.

These tests verify the IEssayRepository interface is properly defined
in the job-agent-platform-contracts package.
"""

import pytest
from typing import Protocol


class TestIEssayRepositoryInterface:
    """Tests for IEssayRepository interface definition."""

    def test_interface_exists(self):
        """Test that IEssayRepository interface exists in contracts package."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        assert IEssayRepository is not None

    def test_interface_is_protocol(self):
        """Test that IEssayRepository is a Protocol."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        assert issubclass(IEssayRepository, Protocol)

    def test_interface_has_create_method(self):
        """Test that interface defines create method."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        assert hasattr(IEssayRepository, "create")

    def test_interface_has_get_by_id_method(self):
        """Test that interface defines get_by_id method."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        assert hasattr(IEssayRepository, "get_by_id")

    def test_interface_has_get_all_method(self):
        """Test that interface defines get_all method."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        assert hasattr(IEssayRepository, "get_all")

    def test_interface_has_delete_method(self):
        """Test that interface defines delete method."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        assert hasattr(IEssayRepository, "delete")

    def test_interface_has_update_method(self):
        """Test that interface defines update method."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        assert hasattr(IEssayRepository, "update")

    def test_interface_cannot_be_instantiated_directly(self):
        """Test that IEssayRepository cannot be instantiated directly."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        with pytest.raises(TypeError):
            IEssayRepository()

    def test_interface_is_importable_from_contracts_root(self):
        """Test that IEssayRepository can be imported from contracts package root."""
        from job_agent_platform_contracts import IEssayRepository

        assert IEssayRepository is not None


class TestEssayRepositoryExceptions:
    """Tests for essay repository exceptions."""

    def test_essay_repository_error_exists(self):
        """Test that EssayRepositoryError exception exists."""
        from job_agent_platform_contracts.essay_repository import EssayRepositoryError

        assert EssayRepositoryError is not None

    def test_essay_not_found_error_exists(self):
        """Test that EssayNotFoundError exception exists."""
        from job_agent_platform_contracts.essay_repository import EssayNotFoundError

        assert EssayNotFoundError is not None

    def test_essay_validation_error_exists(self):
        """Test that EssayValidationError exception exists."""
        from job_agent_platform_contracts.essay_repository import EssayValidationError

        assert EssayValidationError is not None

    def test_essay_not_found_error_stores_essay_id(self):
        """Test that EssayNotFoundError stores the essay_id."""
        from job_agent_platform_contracts.essay_repository import EssayNotFoundError

        error = EssayNotFoundError(essay_id=42)
        assert error.essay_id == 42
        assert "42" in str(error)

    def test_essay_validation_error_stores_field_and_message(self):
        """Test that EssayValidationError stores field and message."""
        from job_agent_platform_contracts.essay_repository import EssayValidationError

        error = EssayValidationError(field="answer", message="is required")
        assert error.field == "answer"
        assert error.message == "is required"
        assert "answer" in str(error)

    def test_essay_repository_error_extends_repository_error(self):
        """Test that EssayRepositoryError extends RepositoryError."""
        from job_agent_platform_contracts.essay_repository import EssayRepositoryError
        from job_agent_platform_contracts.job_repository.exceptions import RepositoryError

        assert issubclass(EssayRepositoryError, RepositoryError)

    def test_essay_not_found_error_extends_essay_repository_error(self):
        """Test that EssayNotFoundError extends EssayRepositoryError."""
        from job_agent_platform_contracts.essay_repository import (
            EssayNotFoundError,
            EssayRepositoryError,
        )

        assert issubclass(EssayNotFoundError, EssayRepositoryError)


class TestEssaySchemas:
    """Tests for essay schemas availability from contracts."""

    def test_essay_create_is_importable(self):
        """Test that EssayCreate schema is importable."""
        from job_agent_platform_contracts.essay_repository import EssayCreate

        assert EssayCreate is not None

    def test_essay_update_is_importable(self):
        """Test that EssayUpdate schema is importable."""
        from job_agent_platform_contracts.essay_repository import EssayUpdate

        assert EssayUpdate is not None

    def test_essay_schema_is_importable(self):
        """Test that Essay response schema is importable."""
        from job_agent_platform_contracts.essay_repository import Essay

        assert Essay is not None
