"""Tests for dependency injection container."""

from unittest.mock import patch, MagicMock


from jobs_repository.container import JobsRepositoryContainer, container, get_job_repository
from jobs_repository.repository.job_repository import JobRepository
from job_agent_platform_contracts import IJobRepository


class TestJobsRepositoryContainer:
    """Test suite for JobsRepositoryContainer."""

    def test_session_factory_is_singleton(self):
        """Test that session_factory is configured as Singleton."""
        test_container = JobsRepositoryContainer()

        with patch("jobs_repository.database.session.get_engine") as mock_engine:
            mock_engine.return_value = MagicMock()

            factory1 = test_container.session_factory()
            factory2 = test_container.session_factory()

            assert factory1 is factory2

    def test_job_repository_is_factory(self):
        """Test that job_repository creates new instances."""
        test_container = JobsRepositoryContainer()

        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_factory.return_value = MagicMock()

            repo1 = test_container.job_repository()
            repo2 = test_container.job_repository()

            assert isinstance(repo1, JobRepository)
            assert isinstance(repo2, JobRepository)
            assert repo1 is not repo2


class TestGetJobRepository:
    """Test suite for get_job_repository function."""

    def test_returns_job_repository_instance(self):
        """Test that get_job_repository returns JobRepository instance."""
        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_factory.return_value = MagicMock()

            repo = get_job_repository()

            assert isinstance(repo, JobRepository)

    def test_returns_ijob_repository_interface(self):
        """Test that get_job_repository returns IJobRepository interface."""
        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_factory.return_value = MagicMock()

            repo = get_job_repository()

            assert isinstance(repo, IJobRepository)

    def test_creates_new_repository_instance(self):
        """Test that get_job_repository creates new instance each time."""
        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_factory.return_value = MagicMock()

            repo1 = get_job_repository()
            repo2 = get_job_repository()

            assert repo1 is not repo2

    def test_uses_global_container(self):
        """Test that get_job_repository uses global container instance."""
        with patch.object(container, "job_repository") as mock_provider:
            mock_repo = MagicMock(spec=IJobRepository)
            mock_provider.return_value = mock_repo

            get_job_repository()

            mock_provider.assert_called_once()
