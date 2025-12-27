"""Tests for dependency injection container.

These tests verify the DI container is properly configured and
exports the get_essay_repository function.
"""

from unittest.mock import MagicMock

from dependency_injector import providers


class TestEssayRepositoryContainer:
    """Test suite for EssayRepositoryContainer."""

    def test_container_exists(self):
        """Test that EssayRepositoryContainer class exists."""
        from essay_repository.container import EssayRepositoryContainer

        assert EssayRepositoryContainer is not None

    def test_session_factory_is_singleton(self):
        """Test that session_factory is configured as Singleton."""
        from essay_repository.container import EssayRepositoryContainer

        test_container = EssayRepositoryContainer()
        mock_factory = MagicMock()

        test_container.session_factory.override(providers.Object(mock_factory))
        try:
            factory1 = test_container.session_factory()
            factory2 = test_container.session_factory()
            assert factory1 is factory2
        finally:
            test_container.session_factory.reset_override()

    def test_essay_repository_is_factory(self):
        """Test that essay_repository creates new instances."""
        from essay_repository.container import EssayRepositoryContainer
        from essay_repository.repository import EssayRepository

        test_container = EssayRepositoryContainer()
        mock_factory = MagicMock()

        test_container.session_factory.override(providers.Object(mock_factory))
        try:
            repo1 = test_container.essay_repository()
            repo2 = test_container.essay_repository()
            assert isinstance(repo1, EssayRepository)
            assert isinstance(repo2, EssayRepository)
            assert repo1 is not repo2
        finally:
            test_container.session_factory.reset_override()


class TestGetEssayRepository:
    """Test suite for get_essay_repository function."""

    def test_get_essay_repository_exists(self):
        """Test that get_essay_repository function exists."""
        from essay_repository.container import get_essay_repository

        assert get_essay_repository is not None
        assert callable(get_essay_repository)

    def test_get_essay_repository_returns_repository_instance(self):
        """Test that get_essay_repository returns IEssayRepository instance."""
        from essay_repository.container import get_essay_repository, container
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        mock_factory = MagicMock()
        container.session_factory.override(providers.Object(mock_factory))
        try:
            repo = get_essay_repository()
            assert isinstance(repo, IEssayRepository)
        finally:
            container.session_factory.reset_override()

    def test_get_essay_repository_creates_new_instance(self):
        """Test that get_essay_repository creates new instance each time."""
        from essay_repository.container import get_essay_repository, container

        mock_factory = MagicMock()
        container.session_factory.override(providers.Object(mock_factory))
        try:
            repo1 = get_essay_repository()
            repo2 = get_essay_repository()
            assert repo1 is not repo2
        finally:
            container.session_factory.reset_override()


class TestContainerConfiguration:
    """Tests for container provider configuration."""

    def test_container_has_session_factory_provider(self):
        """Test that container has session_factory provider."""
        from essay_repository.container import EssayRepositoryContainer

        test_container = EssayRepositoryContainer()
        assert hasattr(test_container, "session_factory")

    def test_container_has_essay_repository_provider(self):
        """Test that container has essay_repository provider."""
        from essay_repository.container import EssayRepositoryContainer

        test_container = EssayRepositoryContainer()
        assert hasattr(test_container, "essay_repository")

    def test_container_has_config_provider(self):
        """Test that container has config provider."""
        from essay_repository.container import EssayRepositoryContainer

        test_container = EssayRepositoryContainer()
        assert hasattr(test_container, "config")


class TestPackageExports:
    """Tests for package-level exports."""

    def test_get_essay_repository_is_exported_from_package(self):
        """Test that get_essay_repository is accessible from package root."""
        from essay_repository import get_essay_repository

        assert get_essay_repository is not None
        assert callable(get_essay_repository)

    def test_essay_repository_class_is_exported(self):
        """Test that EssayRepository class is accessible."""
        from essay_repository import EssayRepository

        assert EssayRepository is not None
