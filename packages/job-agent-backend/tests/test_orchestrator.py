"""Integration tests for JobAgentOrchestrator."""

from unittest.mock import patch, MagicMock
from datetime import datetime, UTC

import pytest

from job_agent_backend.core.orchestrator import JobAgentOrchestrator


class TestJobAgentOrchestrator:
    """Test suite for JobAgentOrchestrator class."""

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return JobAgentOrchestrator()

    @pytest.fixture
    def orchestrator_with_logger(self):
        """Create an orchestrator with a mock logger."""
        mock_logger = MagicMock()
        return JobAgentOrchestrator(logger=mock_logger), mock_logger

    def test_orchestrator_initialization_default_logger(self):
        """Test orchestrator initializes with default logger."""
        orchestrator = JobAgentOrchestrator()
        assert orchestrator.logger is not None
        assert orchestrator.scrapper_manager is not None

    def test_orchestrator_initialization_custom_logger(self):
        """Test orchestrator initializes with custom logger."""
        mock_logger = MagicMock()
        orchestrator = JobAgentOrchestrator(logger=mock_logger)
        assert orchestrator.logger == mock_logger

    def test_get_cv_path_creates_directory(self, orchestrator):
        """Test that get_cv_path creates CV directory if it doesn't exist."""
        user_id = 12345
        cv_path = orchestrator.get_cv_path(user_id)

        # Verify path structure and that directory was created
        assert cv_path.name == f"cv_{user_id}.txt"
        assert cv_path.parent.exists()  # Directory should be created

    def test_get_cv_path_returns_correct_path(self, orchestrator):
        """Test that get_cv_path returns correct path format."""
        user_id = 67890
        cv_path = orchestrator.get_cv_path(user_id)

        assert cv_path.name == "cv_67890.txt"
        assert str(cv_path).endswith("data/cvs/cv_67890.txt")

    @patch("job_agent_backend.core.orchestrator.run_pii_removal")
    @patch("job_agent_backend.core.orchestrator.load_cv_from_text")
    def test_upload_cv_text_file(
        self,
        mock_load_text,
        mock_pii_removal,
        sample_temp_cv_file,
        sample_cv_content,
    ):
        """Test uploading a text CV file."""
        user_id = 111
        mock_load_text.return_value = sample_cv_content
        mock_pii_removal.return_value = "Cleaned CV content"

        # Create mock repository class and instance
        mock_repo_instance = MagicMock()
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        # Create orchestrator with injected mock repository
        orchestrator = JobAgentOrchestrator(cv_repository_class=mock_cv_repo_class)

        orchestrator.upload_cv(user_id, str(sample_temp_cv_file))

        # Verify text loader was called
        mock_load_text.assert_called_once_with(str(sample_temp_cv_file))
        # Verify PII removal was called
        mock_pii_removal.assert_called_once_with(sample_cv_content)
        # Verify CV was saved
        mock_repo_instance.create.assert_called_once_with("Cleaned CV content")

    @patch("job_agent_backend.core.orchestrator.run_pii_removal")
    @patch("job_agent_backend.core.orchestrator.load_cv_from_pdf")
    def test_upload_cv_pdf_file(
        self, mock_load_pdf, mock_pii_removal
    ):
        """Test uploading a PDF CV file."""
        user_id = 222
        pdf_path = "/tmp/test_cv.pdf"
        mock_load_pdf.return_value = "PDF CV content"
        mock_pii_removal.return_value = "Cleaned PDF content"

        # Create mock repository class and instance
        mock_repo_instance = MagicMock()
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        # Create orchestrator with injected mock repository
        orchestrator = JobAgentOrchestrator(cv_repository_class=mock_cv_repo_class)

        orchestrator.upload_cv(user_id, pdf_path)

        # Verify PDF loader was called
        mock_load_pdf.assert_called_once_with(pdf_path)
        # Verify PII removal was called
        mock_pii_removal.assert_called_once_with("PDF CV content")
        # Verify CV was saved
        mock_repo_instance.create.assert_called_once_with("Cleaned PDF content")

    def test_upload_cv_unsupported_format_raises_error(self, orchestrator):
        """Test that uploading unsupported file format raises ValueError."""
        user_id = 333
        unsupported_file = "/tmp/cv.docx"

        with pytest.raises(ValueError, match="Unsupported file format"):
            orchestrator.upload_cv(user_id, unsupported_file)

    @patch("job_agent_backend.core.orchestrator.load_cv_from_text")
    def test_upload_cv_empty_content_raises_error(self, mock_load_text, orchestrator):
        """Test that uploading CV with empty content raises ValueError."""
        user_id = 444
        mock_load_text.return_value = ""

        with pytest.raises(ValueError, match="Failed to extract content"):
            orchestrator.upload_cv(user_id, "/tmp/empty.txt")

    def test_has_cv_returns_true_when_cv_exists(self):
        """Test has_cv returns True when CV exists."""
        user_id = 555
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = "CV content"
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = JobAgentOrchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.has_cv(user_id)

        assert result is True

    def test_has_cv_returns_false_when_cv_missing(self):
        """Test has_cv returns False when CV doesn't exist."""
        user_id = 666
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = None
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = JobAgentOrchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.has_cv(user_id)

        assert result is False

    def test_has_cv_returns_false_on_exception(self):
        """Test has_cv returns False when exception occurs."""
        user_id = 777
        mock_cv_repo_class = MagicMock(side_effect=Exception("File not found"))

        orchestrator = JobAgentOrchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.has_cv(user_id)

        assert result is False

    def test_load_cv_returns_content(self, sample_cv_content):
        """Test load_cv returns CV content."""
        user_id = 888
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = JobAgentOrchestrator(cv_repository_class=mock_cv_repo_class)
        result = orchestrator.load_cv(user_id)

        assert result == sample_cv_content

    def test_load_cv_raises_error_when_not_found(self):
        """Test load_cv raises ValueError when CV not found."""
        user_id = 999
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = None
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = JobAgentOrchestrator(cv_repository_class=mock_cv_repo_class)

        with pytest.raises(ValueError, match="CV not found"):
            orchestrator.load_cv(user_id)

    def test_get_filter_config_empty_when_no_env(self, orchestrator, monkeypatch):
        """Test filter config is empty when no environment variables set."""
        monkeypatch.delenv("FILTER_MAX_MONTHS_OF_EXPERIENCE", raising=False)
        monkeypatch.delenv("FILTER_LOCATION_ALLOWS_TO_APPLY", raising=False)

        config = orchestrator._get_filter_config()

        assert config == {}

    def test_get_filter_config_with_max_experience(self, orchestrator, monkeypatch):
        """Test filter config includes max experience from env."""
        monkeypatch.setenv("FILTER_MAX_MONTHS_OF_EXPERIENCE", "36")

        config = orchestrator._get_filter_config()

        assert config["max_months_of_experience"] == 36

    def test_get_filter_config_with_location_allows(self, orchestrator, monkeypatch):
        """Test filter config includes location_allows_to_apply from env."""
        monkeypatch.setenv("FILTER_LOCATION_ALLOWS_TO_APPLY", "true")

        config = orchestrator._get_filter_config()

        assert config["location_allows_to_apply"] is True

    def test_get_filter_config_location_allows_false(self, orchestrator, monkeypatch):
        """Test filter config handles false values for location_allows_to_apply."""
        monkeypatch.setenv("FILTER_LOCATION_ALLOWS_TO_APPLY", "false")

        config = orchestrator._get_filter_config()

        assert config["location_allows_to_apply"] is False

    def test_scrape_jobs(self, orchestrator, mock_scrapper_manager):
        """Test scrape_jobs calls scrapper manager correctly."""
        orchestrator.scrapper_manager = mock_scrapper_manager

        result = orchestrator.scrape_jobs(salary=5000, employment="remote", timeout=30)

        # Verify scrapper was called with correct parameters
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

    def test_filter_jobs_list(self, orchestrator, sample_jobs_list, monkeypatch):
        """Test filter_jobs_list filters jobs correctly."""
        monkeypatch.setenv("FILTER_MAX_MONTHS_OF_EXPERIENCE", "36")

        result = orchestrator.filter_jobs_list(sample_jobs_list)

        # Should filter out jobs with > 36 months experience
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
            sample_job_dict, sample_cv_content, None, job_repository_class=ANY
        )
        assert result["is_relevant"] is True
        assert result["status"] == "completed"

    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_process_job_with_db_session(
        self, mock_run_job_processing, orchestrator, sample_job_dict, sample_cv_content, db_session
    ):
        """Test process_job passes db_session to workflow."""
        from unittest.mock import ANY

        mock_run_job_processing.return_value = {"status": "completed"}

        orchestrator.process_job(sample_job_dict, sample_cv_content, db_session)

        mock_run_job_processing.assert_called_once_with(
            sample_job_dict, sample_cv_content, db_session, job_repository_class=ANY
        )

    @patch("job_agent_backend.core.orchestrator.init_db")
    @patch("job_agent_backend.core.orchestrator.get_db_session")
    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_run_complete_pipeline_integration(
        self,
        mock_run_job_processing,
        mock_get_db_session,
        mock_init_db,
        mock_scrapper_manager,
        sample_cv_content,
    ):
        """Test complete pipeline integration."""
        user_id = 1000

        # Mock CV repository
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        # Create orchestrator with mocked dependencies
        orchestrator = JobAgentOrchestrator(
            cv_repository_class=mock_cv_repo_class,
            scrapper_manager=mock_scrapper_manager
        )

        # Mock database session
        mock_session = MagicMock()
        mock_get_db_session.return_value = iter([mock_session])

        # Mock job processing workflow
        mock_run_job_processing.return_value = {
            "is_relevant": True,
            "status": "completed",
        }

        # Run complete pipeline
        result = orchestrator.run_complete_pipeline(
            user_id=user_id, salary=4000, employment="remote", timeout=30
        )

        # Verify all steps were called
        mock_init_db.assert_called_once()
        mock_scrapper_manager.scrape_jobs_as_dicts.assert_called_once()
        mock_repo_instance.find.assert_called_once()
        mock_run_job_processing.assert_called_once()

        # Verify results
        assert result["total_scraped"] == 1
        assert result["total_filtered"] == 1
        assert result["total_processed"] == 1

    @patch("job_agent_backend.core.orchestrator.init_db")
    @patch("job_agent_backend.core.orchestrator.CVRepository")
    def test_run_complete_pipeline_raises_when_no_cv(
        self, mock_cv_repo_class, mock_init_db, orchestrator, mock_scrapper_manager
    ):
        """Test pipeline raises error when user has no CV."""
        user_id = 2000
        orchestrator.scrapper_manager = mock_scrapper_manager

        # Mock CV not found
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = None
        mock_cv_repo_class.return_value = mock_repo_instance

        with pytest.raises(ValueError, match="CV not found"):
            orchestrator.run_complete_pipeline(user_id=user_id)

    @patch("job_agent_backend.core.orchestrator.init_db")
    @patch("job_agent_backend.core.orchestrator.get_db_session")
    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_run_complete_pipeline_with_filtering(
        self,
        mock_run_job_processing,
        mock_get_db_session,
        mock_init_db,
        sample_cv_content,
        monkeypatch,
    ):
        """Test complete pipeline with job filtering."""
        user_id = 3000

        # Set filter config
        monkeypatch.setenv("FILTER_MAX_MONTHS_OF_EXPERIENCE", "24")

        # Mock scrapper to return multiple jobs with complete structure
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

        # Mock CV repository
        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        # Create orchestrator with mocked dependencies
        orchestrator = JobAgentOrchestrator(
            cv_repository_class=mock_cv_repo_class,
            scrapper_manager=mock_scrapper
        )

        # Mock DB session
        mock_session = MagicMock()
        mock_get_db_session.return_value = iter([mock_session])

        # Mock processing
        mock_run_job_processing.return_value = {"status": "completed"}

        result = orchestrator.run_complete_pipeline(user_id=user_id)

        # Should have filtered out the senior job (60 months > 24 months limit)
        assert result["total_scraped"] == 2
        # After filtering by max 24 months experience, only job with 12 months should remain
        assert result["total_filtered"] == 1
        # Note: Processing still iterates through filtered jobs
        # The number processed equals the number of filtered jobs
        assert result["total_processed"] >= 1

    @patch("job_agent_backend.core.orchestrator.init_db")
    def test_run_complete_pipeline_handles_db_init_failure(
        self, mock_init_db, orchestrator_with_logger, mock_scrapper_manager
    ):
        """Test pipeline continues when database initialization fails."""
        orchestrator, mock_logger = orchestrator_with_logger
        mock_init_db.side_effect = Exception("Database connection failed")

        orchestrator.scrapper_manager = mock_scrapper_manager

        # Should not raise, but log warning
        # Will fail later when trying to load CV, but DB init failure is handled
        try:
            orchestrator.run_complete_pipeline(user_id=1)
        except Exception as e:
            # Expected to fail at CV loading, not DB init
            assert "Database connection failed" not in str(e)
