"""Tests for dependency injection container."""

from unittest.mock import MagicMock

from dependency_injector import providers

from jobs_repository.container import JobsRepositoryContainer, get_job_repository, container
from jobs_repository.repository.job_repository import JobRepository


class TestJobsRepositoryContainer:
    """Test suite for JobsRepositoryContainer."""

    def test_session_factory_is_singleton(self):
        """Test that session_factory is configured as Singleton."""
        test_container = JobsRepositoryContainer()
        mock_factory = MagicMock()

        test_container.session_factory.override(providers.Object(mock_factory))
        try:
            factory1 = test_container.session_factory()
            factory2 = test_container.session_factory()

            assert factory1 is factory2
        finally:
            test_container.session_factory.reset_override()

    def test_job_repository_is_factory(self):
        """Test that job_repository creates new instances."""
        test_container = JobsRepositoryContainer()
        mock_factory = MagicMock()

        test_container.session_factory.override(providers.Object(mock_factory))
        try:
            repo1 = test_container.job_repository()
            repo2 = test_container.job_repository()

            assert isinstance(repo1, JobRepository)
            assert isinstance(repo2, JobRepository)
            assert repo1 is not repo2
        finally:
            test_container.session_factory.reset_override()


class TestGetJobRepository:
    """Test suite for get_job_repository function."""

    def test_returns_job_repository_instance(self):
        """Test that get_job_repository returns JobRepository instance."""
        mock_factory = MagicMock()

        container.session_factory.override(providers.Object(mock_factory))
        try:
            repo = get_job_repository()

            assert isinstance(repo, JobRepository)
        finally:
            container.session_factory.reset_override()

    def test_creates_new_repository_instance(self):
        """Test that get_job_repository creates new instance each time."""
        mock_factory = MagicMock()

        container.session_factory.override(providers.Object(mock_factory))
        try:
            repo1 = get_job_repository()
            repo2 = get_job_repository()

            assert repo1 is not repo2
        finally:
            container.session_factory.reset_override()
