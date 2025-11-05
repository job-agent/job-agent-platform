"""Integration tests for JobAgentOrchestrator."""

from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
import sys

import pytest
from dependency_injector import providers


sys.modules["scrapper_service"] = MagicMock()
sys.modules["djinni_scrapper"] = MagicMock()
sys.modules["djinni_scrapper.scrapper"] = MagicMock()


from job_agent_backend.container import ApplicationContainer  # noqa: E402
from job_agent_backend.filter_service.filter import FilterService  # noqa: E402


class TestJobAgentOrchestrator:
    """Test suite for JobAgentOrchestrator class."""

    @pytest.fixture
    def app_container(self):
        """Provide a fresh dependency container per test."""
        container = ApplicationContainer()

        class StubRepository:
            def get_by_external_id(self, external_id, source=None):
                return None

            def has_active_job_with_title_and_company(self, title, company_name):
                return False

        container.job_repository_factory.override(providers.Object(lambda: StubRepository()))

        container.filter_service.override(
            providers.Singleton(
                FilterService,
                job_repository_factory=container.job_repository_factory,
            )
        )

        return container

    @pytest.fixture
    def orchestrator(self, app_container):
        """Create an orchestrator instance."""
        return app_container.orchestrator(database_initializer=lambda: None)

    @pytest.fixture
    def orchestrator_with_logger(self, app_container):
        """Create an orchestrator with a mock logger."""
        mock_logger = MagicMock()
        orchestrator = app_container.orchestrator(
            logger=mock_logger,
            database_initializer=lambda: None,
        )
        return orchestrator, mock_logger

    def test_orchestrator_initialization_default_logger(self, app_container):
        """Test orchestrator initializes with default logger."""
        orchestrator = app_container.orchestrator()
        assert orchestrator.logger is not None
        assert orchestrator.scrapper_manager is not None

    def test_orchestrator_initialization_custom_logger(self, app_container):
        """Test orchestrator initializes with custom logger."""
        mock_logger = MagicMock()
        orchestrator = app_container.orchestrator(logger=mock_logger)
        assert orchestrator.logger == mock_logger

    def test_get_cv_path_creates_directory(self, orchestrator):
        """Test that get_cv_path creates CV directory if it doesn't exist."""
        user_id = 12345
        cv_path = orchestrator.get_cv_path(user_id)

        assert cv_path.name == f"cv_{user_id}.txt"
        assert cv_path.parent.exists()

    def test_get_cv_path_returns_correct_path(self, orchestrator):
        """Test that get_cv_path returns correct path format."""
        user_id = 67890
        cv_path = orchestrator.get_cv_path(user_id)

        assert cv_path.name == "cv_67890.txt"
        assert str(cv_path).endswith("data/cvs/cv_67890.txt")

    @patch("job_agent_backend.core.orchestrator.run_pii_removal")
    def test_upload_cv_text_file(
        self,
        mock_pii_removal,
        sample_temp_cv_file,
        sample_cv_content,
        app_container,
    ):
        """Test uploading a text CV file."""
        user_id = 111
        mock_pii_removal.return_value = "Cleaned CV content"

        mock_repo_instance = MagicMock()
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        mock_cv_loader = MagicMock()
        mock_cv_loader.load_from_text.return_value = sample_cv_content

        orchestrator = app_container.orchestrator(
            cv_repository_class=mock_cv_repo_class,
            cv_loader=mock_cv_loader,
        )

        orchestrator.upload_cv(user_id, str(sample_temp_cv_file))

        mock_cv_loader.load_from_text.assert_called_once_with(str(sample_temp_cv_file))

        mock_pii_removal.assert_called_once_with(sample_cv_content)

        mock_repo_instance.create.assert_called_once_with("Cleaned CV content")

    @patch("job_agent_backend.core.orchestrator.run_pii_removal")
    def test_upload_cv_pdf_file(self, mock_pii_removal, app_container):
        """Test uploading a PDF CV file."""
        user_id = 222
        pdf_path = "/tmp/test_cv.pdf"
        mock_pii_removal.return_value = "Cleaned PDF content"

        mock_repo_instance = MagicMock()
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        mock_cv_loader = MagicMock()
        mock_cv_loader.load_from_pdf.return_value = "PDF CV content"

        orchestrator = app_container.orchestrator(
            cv_repository_class=mock_cv_repo_class,
            cv_loader=mock_cv_loader,
        )

        orchestrator.upload_cv(user_id, pdf_path)

        mock_cv_loader.load_from_pdf.assert_called_once_with(pdf_path)

        mock_pii_removal.assert_called_once_with("PDF CV content")

        mock_repo_instance.create.assert_called_once_with("Cleaned PDF content")

    def test_upload_cv_unsupported_format_raises_error(self, orchestrator):
        """Test that uploading unsupported file format raises ValueError."""
        user_id = 333
        unsupported_file = "/tmp/cv.docx"

        with pytest.raises(ValueError, match="Unsupported file format"):
            orchestrator.upload_cv(user_id, unsupported_file)

    def test_upload_cv_empty_content_raises_error(self, app_container):
        """Test that uploading CV with empty content raises ValueError."""
        user_id = 444

        mock_cv_loader = MagicMock()
        mock_cv_loader.load_from_text.return_value = ""

        orchestrator = app_container.orchestrator(cv_loader=mock_cv_loader)

        with pytest.raises(ValueError, match="Failed to extract content"):
            orchestrator.upload_cv(user_id, "/tmp/empty.txt")

    def test_has_cv_returns_true_when_cv_exists(self, app_container):
        """Test has_cv returns True when CV exists."""
        user_id = 555
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = "CV content"
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = app_container.orchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.has_cv(user_id)

        assert result is True

    def test_has_cv_returns_false_when_cv_missing(self, app_container):
        """Test has_cv returns False when CV doesn't exist."""
        user_id = 666
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = None
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = app_container.orchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.has_cv(user_id)

        assert result is False

    def test_has_cv_returns_false_on_exception(self, app_container):
        """Test has_cv returns False when exception occurs."""
        user_id = 777
        mock_cv_repo_class = MagicMock(side_effect=Exception("File not found"))

        orchestrator = app_container.orchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.has_cv(user_id)

        assert result is False

    def test_load_cv_returns_content(self, sample_cv_content, app_container):
        """Test load_cv returns CV content."""
        user_id = 888
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = app_container.orchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.load_cv(user_id)

        assert result == sample_cv_content

    def test_load_cv_raises_error_when_not_found(self, app_container):
        """Test load_cv raises ValueError when CV not found."""
        user_id = 999
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = None
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = app_container.orchestrator(cv_repository_class=mock_cv_repo_class)

        with pytest.raises(ValueError, match="CV not found"):
            orchestrator.load_cv(user_id)

    def test_scrape_jobs(self, orchestrator, mock_scrapper_manager):
        """Test scrape_jobs calls scrapper manager correctly."""
        orchestrator.scrapper_manager = mock_scrapper_manager

        result = orchestrator.scrape_jobs(salary=5000, employment="remote", timeout=30)

        mock_scrapper_manager.scrape_jobs_as_dicts.assert_called_once_with(
            salary=5000, employment="remote", posted_after=None, timeout=30
        )
        assert len(result) == 1
        assert result[0]["title"] == "Python Developer"

    def test_scrape_jobs_with_posted_after(self, orchestrator, mock_scrapper_manager):
        """Test scrape_jobs with posted_after date."""
        orchestrator.scrapper_manager = mock_scrapper_manager
        posted_after = datetime(2024, 1, 1, tzinfo=UTC)

        orchestrator.scrape_jobs(salary=4000, posted_after=posted_after)

        mock_scrapper_manager.scrape_jobs_as_dicts.assert_called_once()
        call_kwargs = mock_scrapper_manager.scrape_jobs_as_dicts.call_args[1]
        assert call_kwargs["posted_after"] == posted_after

    def test_filter_jobs_list(self, orchestrator, sample_jobs_list):
        """Test filter_jobs_list filters jobs correctly."""
        orchestrator.filter_service.configure({"max_months_of_experience": 36})

        result = orchestrator.filter_jobs_list(sample_jobs_list)

        assert len(result) == 2
        assert all(job["experience_months"] <= 36 for job in result)

    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_process_job(
        self, mock_run_job_processing, orchestrator, sample_job_dict, sample_cv_content
    ):
        """Test process_job calls workflow correctly."""
        from unittest.mock import ANY

        mock_run_job_processing.return_value = {
            "is_relevant": True,
            "extracted_must_have_skills": ["Python"],
            "status": "completed",
        }

        result = orchestrator.process_job(sample_job_dict, sample_cv_content)

        mock_run_job_processing.assert_called_once_with(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=ANY,
        )
        assert result["is_relevant"] is True
        assert result["status"] == "completed"

    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_process_job_with_custom_repository_factory(
        self,
        mock_run_job_processing,
        app_container,
        sample_job_dict,
        sample_cv_content,
    ):
        """Test process_job forwards custom repository factory."""

        mock_factory = MagicMock()
        orchestrator = app_container.orchestrator(job_repository_factory=mock_factory)

        mock_run_job_processing.return_value = {"status": "completed"}

        orchestrator.process_job(sample_job_dict, sample_cv_content)

        mock_run_job_processing.assert_called_once_with(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=mock_factory,
        )

    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_run_complete_pipeline_integration(
        self,
        mock_run_job_processing,
        mock_scrapper_manager,
        sample_cv_content,
        app_container,
    ):
        """Test complete pipeline integration."""
        user_id = 1000

        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        mock_initializer = MagicMock()

        orchestrator = app_container.orchestrator(
            cv_repository_class=mock_cv_repo_class,
            scrapper_manager=mock_scrapper_manager,
            database_initializer=mock_initializer,
        )

        mock_run_job_processing.return_value = {
            "is_relevant": True,
            "status": "completed",
        }

        result = orchestrator.run_complete_pipeline(
            user_id=user_id, salary=4000, employment="remote", timeout=30
        )

        mock_initializer.assert_called_once()
        mock_scrapper_manager.scrape_jobs_as_dicts.assert_called_once()
        mock_repo_instance.find.assert_called_once()
        mock_run_job_processing.assert_called_once()

        assert result["total_scraped"] == 1
        assert result["total_filtered"] == 1
        assert result["total_processed"] == 1

    @patch("job_agent_backend.core.orchestrator.CVRepository")
    def test_run_complete_pipeline_raises_when_no_cv(
        self,
        mock_cv_repo_class,
        orchestrator,
        mock_scrapper_manager,
    ):
        """Test pipeline raises error when user has no CV."""
        user_id = 2000
        orchestrator.scrapper_manager = mock_scrapper_manager

        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = None
        mock_cv_repo_class.return_value = mock_repo_instance

        with pytest.raises(ValueError, match="CV not found"):
            orchestrator.run_complete_pipeline(user_id=user_id)

    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_run_complete_pipeline_with_filtering(
        self,
        mock_run_job_processing,
        sample_cv_content,
        app_container,
    ):
        """Test complete pipeline with job filtering."""
        user_id = 3000

        mock_scrapper = MagicMock()
        jobs_data = [
            {
                "job_id": 1,
                "title": "Junior Developer",
                "description": "Junior position",
                "experience_months": 12.0,
                "location": {"region": "Remote", "can_apply": True},
                "company": {"name": "Company A"},
                "category": "Software",
                "url": "https://example.com/1",
                "date_posted": "2024-01-15T10:00:00Z",
                "employment_type": "FULL_TIME",
            },
            {
                "job_id": 2,
                "title": "Senior Developer",
                "description": "Senior position",
                "experience_months": 60.0,
                "location": {"region": "Remote", "can_apply": True},
                "company": {"name": "Company B"},
                "category": "Software",
                "url": "https://example.com/2",
                "date_posted": "2024-01-15T10:00:00Z",
                "employment_type": "FULL_TIME",
            },
        ]
        mock_scrapper.scrape_jobs_as_dicts.return_value = jobs_data

        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = app_container.orchestrator(
            cv_repository_class=mock_cv_repo_class,
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        orchestrator.filter_service.configure({"max_months_of_experience": 24})

        mock_run_job_processing.return_value = {"status": "completed"}

        result = orchestrator.run_complete_pipeline(user_id=user_id)

        assert result["total_scraped"] == 2

        assert result["total_filtered"] == 1

        assert result["total_processed"] >= 1

    def test_run_complete_pipeline_handles_db_init_failure(
        self,
        orchestrator_with_logger,
        mock_scrapper_manager,
    ):
        """Test pipeline continues when database initialization fails."""
        orchestrator, mock_logger = orchestrator_with_logger
        mock_initializer = MagicMock(side_effect=Exception("Database connection failed"))
        orchestrator.database_initializer = mock_initializer

        orchestrator.scrapper_manager = mock_scrapper_manager

        try:
            orchestrator.run_complete_pipeline(user_id=1)
        except Exception as e:
            assert "Database connection failed" not in str(e)
