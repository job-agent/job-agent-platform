"""Tests for dependency injection container."""

from unittest.mock import patch, MagicMock


from jobs_repository.container import JobsRepositoryContainer, container, get_job_repository
from jobs_repository.repository.job_repository import JobRepository
from job_agent_platform_contracts import IJobRepository


class TestJobsRepositoryContainer:
    """Test suite for JobsRepositoryContainer."""

    def test_container_has_session_factory_provider(self):
        """Test that container has session_factory provider."""
        test_container = JobsRepositoryContainer()

        assert hasattr(test_container, "session_factory")

    def test_container_has_job_repository_provider(self):
        """Test that container has job_repository provider."""
        test_container = JobsRepositoryContainer()

        assert hasattr(test_container, "job_repository")

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

    def test_job_repository_receives_session_factory(self):
        """Test that job_repository is initialized with session_factory."""
        test_container = JobsRepositoryContainer()

        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_session_factory = MagicMock()
            mock_factory.return_value = mock_session_factory

            repo = test_container.job_repository()

            assert isinstance(repo, JobRepository)


class TestContainerInstance:
    """Test suite for global container instance."""

    def test_container_has_providers_configured(self):
        """Test that global container has providers configured."""
        assert hasattr(container, "session_factory")
        assert hasattr(container, "job_repository")


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

    def test_repository_has_session_factory_configured(self):
        """Test that returned repository has session_factory configured."""
        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_session_factory = MagicMock()
            mock_factory.return_value = mock_session_factory

            repo = get_job_repository()

            assert repo._session_factory is not None

    def test_handles_callable_repository(self):
        """Test that get_job_repository handles callable return value."""
        with patch.object(container, "job_repository") as mock_provider:
            mock_repo = MagicMock(spec=IJobRepository)
            mock_provider.return_value = mock_repo

            repo = get_job_repository()

            assert repo is mock_repo

    def test_uses_global_container(self):
        """Test that get_job_repository uses global container instance."""
        with patch.object(container, "job_repository") as mock_provider:
            mock_repo = MagicMock(spec=IJobRepository)
            mock_provider.return_value = mock_repo

            get_job_repository()

            mock_provider.assert_called_once()

    def test_repository_can_create_jobs(self):
        """Test that repository from container can create jobs."""
        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_session = MagicMock()
            mock_session_factory = MagicMock(return_value=mock_session)
            mock_factory.return_value = mock_session_factory

            repo = get_job_repository()

            assert hasattr(repo, "create")
            assert callable(repo.create)

    def test_repository_can_get_by_external_id(self):
        """Test that repository from container can get by external_id."""
        with patch("jobs_repository.container.get_session_factory") as mock_factory:
            mock_session = MagicMock()
            mock_session_factory = MagicMock(return_value=mock_session)
            mock_factory.return_value = mock_session_factory

            repo = get_job_repository()

            assert hasattr(repo, "get_by_external_id")
            assert callable(repo.get_by_external_id)
