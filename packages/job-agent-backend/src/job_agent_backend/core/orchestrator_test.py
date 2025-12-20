"""Tests for JobAgentOrchestrator."""

from unittest.mock import patch, MagicMock
import sys

import pytest


sys.modules["scrapper_service"] = MagicMock()


class TestJobAgentOrchestrator:
    """Test suite for JobAgentOrchestrator class."""

    @pytest.fixture
    def app_container(self, app_container_with_stub_repository):
        """Use the shared app container fixture."""
        return app_container_with_stub_repository

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

        # Mock streaming to return a list of lists (batches)
        mock_scrapper_manager.scrape_jobs_streaming.return_value = iter(
            [[{"title": "Python Developer"}]]
        )

        result = orchestrator.scrape_jobs(min_salary=5000, employment_location="remote", timeout=30)

        mock_scrapper_manager.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper_manager.scrape_jobs_streaming.call_args[1]
        assert call_kwargs["min_salary"] == 5000
        assert call_kwargs["employment_location"] == "remote"
        assert call_kwargs["timeout"] == 30
        # posted_after is now auto-calculated (defaults to 5 days ago when no jobs exist)
        assert call_kwargs["posted_after"] is not None
        assert len(result) == 1
        assert result[0]["title"] == "Python Developer"

    def test_scrape_jobs_with_explicit_days(self, orchestrator, mock_scrapper_manager):
        """Test scrape_jobs with explicit days parameter."""
        from datetime import datetime, timedelta, timezone

        orchestrator.scrapper_manager = mock_scrapper_manager

        mock_scrapper_manager.scrape_jobs_streaming.return_value = iter([])

        orchestrator.scrape_jobs(min_salary=4000, days=7)

        mock_scrapper_manager.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper_manager.scrape_jobs_streaming.call_args[1]
        # Verify posted_after is approximately 7 days ago
        expected = datetime.now(timezone.utc) - timedelta(days=7)
        time_diff = abs((call_kwargs["posted_after"] - expected).total_seconds())
        assert time_diff < 60, "posted_after should be ~7 days ago"

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

        # Mock streaming to return one batch with one valid job
        valid_job = {
            "job_id": 1,
            "title": "Python Developer",
            "url": "https://example.com/1",
            "description": "Python dev position",
            "company": {"name": "TechCo", "website": "https://techco.com"},
            "category": "Software Development",
            "date_posted": "2024-01-15T10:00:00Z",
            "valid_through": "2024-02-15T10:00:00Z",
            "employment_type": "FULL_TIME",
            "experience_months": 24.0,
            "location": {"region": "Remote", "is_remote": True, "can_apply": True},
            "industry": "Technology",
        }
        mock_scrapper_manager.scrape_jobs_streaming.return_value = iter([[valid_job]])

        result = orchestrator.run_complete_pipeline(
            user_id=user_id, min_salary=4000, employment_location="remote", timeout=30
        )

        mock_initializer.assert_called_once()
        mock_scrapper_manager.scrape_jobs_streaming.assert_called_once()
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
        mock_scrapper.scrape_jobs_streaming.return_value = iter([jobs_data])

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


class TestOrchestratorFilterJobsListWithRejected:
    """Tests for filter_jobs_list integration with filtered jobs storage.

    These tests verify the NEW behavior where filter_jobs_list:
    1. Uses filter_with_rejected to get both passed and rejected jobs
    2. Calls save_filtered_jobs on the repository with rejected jobs
    3. Returns only the passed jobs for workflow processing
    """

    @pytest.fixture
    def app_container(self, app_container_with_stub_repository):
        """Use the shared app container fixture."""
        return app_container_with_stub_repository

    def test_filter_jobs_list_calls_save_filtered_jobs_with_rejected(
        self, app_container, stub_job_repository, sample_jobs_list
    ):
        """Test that filter_jobs_list calls save_filtered_jobs with rejected jobs.

        When jobs are filtered out by the pre-LLM filter, they should be
        saved to the repository with is_filtered=True, is_relevant=False.
        """
        orchestrator = app_container.orchestrator(database_initializer=lambda: None)
        orchestrator.filter_service.configure({"max_months_of_experience": 36})

        orchestrator.filter_jobs_list(sample_jobs_list)

        # Verify save_filtered_jobs was called with rejected jobs
        assert len(stub_job_repository.saved_filtered_jobs) == 2

        # Verify the rejected jobs are the ones with high experience
        saved_ids = [job["job_id"] for job in stub_job_repository.saved_filtered_jobs]
        assert 3 in saved_ids  # 60 months experience
        assert 4 in saved_ids  # 96 months experience

    def test_filter_jobs_list_returns_only_passed_jobs(self, app_container, sample_jobs_list):
        """Test that filter_jobs_list returns only passed jobs for processing.

        Rejected jobs should be stored but not returned for workflow processing.
        """
        orchestrator = app_container.orchestrator(database_initializer=lambda: None)
        orchestrator.filter_service.configure({"max_months_of_experience": 36})

        result = orchestrator.filter_jobs_list(sample_jobs_list)

        # Only jobs with experience <= 36 should be returned
        result_ids = [job["job_id"] for job in result]
        assert 1 in result_ids  # 12 months
        assert 2 in result_ids  # 36 months
        assert 3 not in result_ids  # 60 months - filtered
        assert 4 not in result_ids  # 96 months - filtered

    def test_filter_jobs_list_does_not_save_when_no_rejections(
        self, app_container, stub_job_repository
    ):
        """Test that save_filtered_jobs is not called when all jobs pass."""
        jobs = [
            {
                "job_id": 1,
                "title": "Junior Dev",
                "experience_months": 12,
                "location": {"can_apply": True},
            },
        ]
        orchestrator = app_container.orchestrator(database_initializer=lambda: None)
        orchestrator.filter_service.configure({"max_months_of_experience": 60})

        result = orchestrator.filter_jobs_list(jobs)

        # No jobs should be saved as filtered
        assert len(stub_job_repository.saved_filtered_jobs) == 0
        assert len(result) == 1

    def test_filter_jobs_list_saves_all_rejected_when_all_fail(
        self, app_container, stub_job_repository
    ):
        """Test that all jobs are saved as filtered when all are rejected."""
        jobs = [
            {
                "job_id": 1,
                "title": "Senior Dev",
                "experience_months": 120,
                "location": {"can_apply": True},
            },
            {
                "job_id": 2,
                "title": "Staff Eng",
                "experience_months": 96,
                "location": {"can_apply": True},
            },
        ]
        orchestrator = app_container.orchestrator(database_initializer=lambda: None)
        orchestrator.filter_service.configure({"max_months_of_experience": 24})

        result = orchestrator.filter_jobs_list(jobs)

        # All jobs should be saved as filtered
        assert len(stub_job_repository.saved_filtered_jobs) == 2
        # No jobs should be returned for processing
        assert len(result) == 0

    def test_filter_jobs_list_logs_filtered_count(self, app_container, sample_jobs_list):
        """Test that filter_jobs_list logs both passed and filtered counts."""
        mock_logger = MagicMock()
        orchestrator = app_container.orchestrator(
            logger=mock_logger,
            database_initializer=lambda: None,
        )
        orchestrator.filter_service.configure({"max_months_of_experience": 36})

        orchestrator.filter_jobs_list(sample_jobs_list)

        # Verify logging was called
        mock_logger.assert_called()
        # Check that the log message contains filter counts
        log_calls = [str(call) for call in mock_logger.call_args_list]
        assert any("2/4" in call or "2" in call for call in log_calls)


class TestOrchestratorPipelineWithFilteredJobsStorage:
    """Integration tests for the complete pipeline with filtered jobs storage.

    These tests verify that the run_complete_pipeline method properly stores
    filtered jobs during the filtering phase.
    """

    @pytest.fixture
    def app_container(self, app_container_with_stub_repository):
        """Use the shared app container fixture."""
        return app_container_with_stub_repository

    @patch("job_agent_backend.core.orchestrator.run_job_processing")
    def test_pipeline_stores_filtered_jobs_before_processing(
        self, mock_run_job_processing, app_container, stub_job_repository, sample_cv_content
    ):
        """Test that filtered jobs are stored before workflow processing begins."""
        user_id = 5000

        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        mock_scrapper = MagicMock()
        jobs_data = [
            {
                "job_id": 1,
                "title": "Junior Developer",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Company A"},
                "url": "https://example.com/1",
                "date_posted": "2024-01-15T10:00:00Z",
                "employment_type": "FULL_TIME",
            },
            {
                "job_id": 2,
                "title": "Senior Developer",
                "experience_months": 120,  # High experience - will be filtered
                "location": {"can_apply": True},
                "company": {"name": "Company B"},
                "url": "https://example.com/2",
                "date_posted": "2024-01-15T10:00:00Z",
                "employment_type": "FULL_TIME",
            },
        ]
        mock_scrapper.scrape_jobs_streaming.return_value = iter([jobs_data])

        orchestrator = app_container.orchestrator(
            cv_repository_class=mock_cv_repo_class,
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )
        orchestrator.filter_service.configure({"max_months_of_experience": 60})

        mock_run_job_processing.return_value = {"status": "completed"}

        result = orchestrator.run_complete_pipeline(user_id=user_id)

        # The filtered job should have been stored
        assert len(stub_job_repository.saved_filtered_jobs) == 1
        assert stub_job_repository.saved_filtered_jobs[0]["job_id"] == 2

        # Only the passing job should have been processed
        assert mock_run_job_processing.call_count == 1

        # Pipeline summary should reflect correct counts
        assert result["total_scraped"] == 2
        assert result["total_filtered"] == 1  # Only 1 passed the filter
        assert result["total_processed"] == 1


class TestOrchestratorDateCalculation:
    """Tests for orchestrator date calculation logic.

    These tests verify the NEW behavior where the orchestrator accepts a `days`
    parameter and auto-calculates `posted_after` from the job repository when
    `days=None`.

    REQ-3: Orchestrator accepts days parameter instead of posted_after
    REQ-4: Orchestrator auto-calculates posted_after when days is None
    REQ-5: Orchestrator converts explicit days to posted_after
    REQ-6: MAX_AUTO_DAYS constant moves to backend
    """

    @pytest.fixture
    def app_container(self, app_container_with_stub_repository):
        """Use the shared app container fixture."""
        return app_container_with_stub_repository

    def test_scrape_jobs_with_explicit_days_converts_to_posted_after(
        self, app_container, stub_job_repository
    ):
        """Orchestrator should convert explicit days=7 to posted_after = now - 7 days.

        REQ-5: When days is explicitly provided, calculate posted_after from it.
        """
        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[{"title": "Test Job"}]])

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call with explicit days=7
        orchestrator.scrape_jobs(days=7)

        # Verify scrapper was called with posted_after approximately 7 days ago
        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None, "posted_after should be set when days is provided"

        # Verify the date is approximately 7 days ago
        from datetime import datetime, timedelta, timezone

        expected = datetime.now(timezone.utc) - timedelta(days=7)
        time_diff = abs((posted_after - expected).total_seconds())
        assert time_diff < 60, f"posted_after should be ~7 days ago, diff={time_diff}s"

    def test_scrape_jobs_with_none_days_auto_calculates_from_repository(
        self, app_container, stub_job_repository
    ):
        """Orchestrator should auto-calculate posted_after from repository when days=None.

        REQ-4: When days is None, query job_repository.get_latest_updated_at().
        """
        from datetime import datetime, timedelta, timezone

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[]])

        # Set up latest job updated 2 days ago
        latest_time = datetime.now(timezone.utc) - timedelta(days=2)
        stub_job_repository.latest_updated_at = latest_time

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call with days=None
        orchestrator.scrape_jobs(days=None)

        # Verify scrapper was called with posted_after approximately 2 days ago
        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None, "posted_after should be auto-calculated"

        # The posted_after should be close to the latest job time
        time_diff = abs((posted_after - latest_time).total_seconds())
        assert time_diff < 60, f"posted_after should match latest job time, diff={time_diff}s"

    def test_scrape_jobs_caps_auto_calculated_at_max_auto_days(
        self, app_container, stub_job_repository
    ):
        """Orchestrator should cap auto-calculated date at MAX_AUTO_DAYS (5 days).

        REQ-4: If latest job is older than MAX_AUTO_DAYS, cap at MAX_AUTO_DAYS.
        """
        from datetime import datetime, timedelta, timezone

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[]])

        # Set up latest job updated 10 days ago (older than 5-day cap)
        old_time = datetime.now(timezone.utc) - timedelta(days=10)
        stub_job_repository.latest_updated_at = old_time

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call with days=None
        orchestrator.scrape_jobs(days=None)

        # Verify scrapper was called with posted_after capped at 5 days
        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None, "posted_after should be set"

        # The posted_after should be approximately 5 days ago (capped)
        expected_cap = datetime.now(timezone.utc) - timedelta(days=5)
        time_diff = abs((posted_after - expected_cap).total_seconds())
        assert time_diff < 60, f"posted_after should be capped at 5 days, diff={time_diff}s"

    def test_scrape_jobs_defaults_to_max_auto_days_when_no_jobs_exist(
        self, app_container, stub_job_repository
    ):
        """Orchestrator should default to MAX_AUTO_DAYS when no jobs exist.

        REQ-4: When get_latest_updated_at returns None, use now - MAX_AUTO_DAYS.
        """
        from datetime import datetime, timedelta, timezone

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[]])

        # No jobs in repository
        stub_job_repository.latest_updated_at = None

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call with days=None
        orchestrator.scrape_jobs(days=None)

        # Verify scrapper was called with posted_after = 5 days ago
        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None, "posted_after should default to 5 days"

        expected_default = datetime.now(timezone.utc) - timedelta(days=5)
        time_diff = abs((posted_after - expected_default).total_seconds())
        assert time_diff < 60, f"posted_after should be 5 days ago, diff={time_diff}s"

    def test_scrape_jobs_streaming_with_explicit_days_converts_to_posted_after(
        self, app_container, stub_job_repository
    ):
        """scrape_jobs_streaming should convert explicit days to posted_after.

        REQ-5: Streaming variant should also support days parameter.
        """
        from datetime import datetime, timedelta, timezone

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[{"title": "Test"}]])

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call streaming with explicit days=3
        list(orchestrator.scrape_jobs_streaming(days=3))

        # Verify the conversion
        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None
        expected = datetime.now(timezone.utc) - timedelta(days=3)
        time_diff = abs((posted_after - expected).total_seconds())
        assert time_diff < 60, f"posted_after should be ~3 days ago, diff={time_diff}s"

    def test_scrape_jobs_streaming_with_none_days_auto_calculates(
        self, app_container, stub_job_repository
    ):
        """scrape_jobs_streaming should auto-calculate when days=None.

        REQ-4: Streaming variant should also support auto-calculation.
        """
        from datetime import datetime, timedelta, timezone

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[]])

        # Set up latest job updated 1 day ago
        latest_time = datetime.now(timezone.utc) - timedelta(days=1)
        stub_job_repository.latest_updated_at = latest_time

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call streaming with days=None
        list(orchestrator.scrape_jobs_streaming(days=None))

        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None
        time_diff = abs((posted_after - latest_time).total_seconds())
        assert time_diff < 60, "posted_after should match latest job time"

    def test_run_complete_pipeline_accepts_days_parameter(
        self, app_container, stub_job_repository, sample_cv_content
    ):
        """run_complete_pipeline should accept days parameter.

        REQ-3: All orchestrator methods should accept days instead of posted_after.
        """
        from datetime import datetime, timedelta, timezone

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[]])

        mock_repo_instance = MagicMock()
        mock_repo_instance.find.return_value = sample_cv_content
        mock_cv_repo_class = MagicMock(return_value=mock_repo_instance)

        orchestrator = app_container.orchestrator(
            cv_repository_class=mock_cv_repo_class,
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call with explicit days=5
        orchestrator.run_complete_pipeline(user_id=1, days=5)

        # Verify scrapper was called with posted_after approximately 5 days ago
        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None
        expected = datetime.now(timezone.utc) - timedelta(days=5)
        time_diff = abs((posted_after - expected).total_seconds())
        assert time_diff < 60, "posted_after should be ~5 days ago"

    def test_scrape_jobs_handles_timezone_naive_repository_timestamp(
        self, app_container, stub_job_repository
    ):
        """Orchestrator should handle timezone-naive timestamps from repository.

        The repository may return timezone-naive datetimes; orchestrator should
        normalize them to UTC.
        """
        from datetime import datetime, timedelta

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[]])

        # Set up latest job with timezone-naive datetime (2 days ago)
        naive_time = datetime.now() - timedelta(days=2)  # No timezone info
        stub_job_repository.latest_updated_at = naive_time

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        # Call with days=None
        orchestrator.scrape_jobs(days=None)

        # Verify the posted_after is timezone-aware
        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None
        assert posted_after.tzinfo is not None, "posted_after should be timezone-aware"

    def test_scrape_jobs_uses_utc_for_explicit_days_calculation(
        self, app_container, stub_job_repository
    ):
        """Orchestrator should use UTC for explicit days calculation.

        All date calculations must use UTC to ensure consistency.
        """
        from datetime import timezone

        mock_scrapper = MagicMock()
        mock_scrapper.scrape_jobs_streaming.return_value = iter([[]])

        orchestrator = app_container.orchestrator(
            scrapper_manager=mock_scrapper,
            database_initializer=lambda: None,
        )

        orchestrator.scrape_jobs(days=1)

        mock_scrapper.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_scrapper.scrape_jobs_streaming.call_args[1]
        posted_after = call_kwargs["posted_after"]

        assert posted_after is not None
        assert posted_after.tzinfo == timezone.utc, "posted_after should be in UTC"
