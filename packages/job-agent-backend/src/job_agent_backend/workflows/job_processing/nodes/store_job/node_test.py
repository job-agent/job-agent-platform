"""Tests for store_job node."""

from unittest.mock import MagicMock

from .node import create_store_job_node


class TestStoreJobNode:
    """Tests for store_job_node function."""

    def test_stores_job_successfully(self):
        """Node stores job to repository and returns status."""
        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        job_repository_factory = MagicMock(return_value=mock_repository)

        store_job_node = create_store_job_node(job_repository_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Python Developer",
                "description": "Some description",
            },
            "status": "in_progress",
            "cv_context": "Python developer",
            "is_relevant": True,
            "extracted_must_have_skills": ["Python", "Django"],
            "extracted_nice_to_have_skills": ["Docker"],
        }

        result = store_job_node(state)

        job_repository_factory.assert_called_once()
        mock_repository.create.assert_called_once()
        created_job = mock_repository.create.call_args[0][0]
        assert created_job["must_have_skills"] == ["Python", "Django"]
        assert created_job["nice_to_have_skills"] == ["Docker"]
        assert result["status"] == "in_progress"

    def test_returns_error_status_on_repository_exception(self):
        """Node returns error status when repository raises exception."""
        mock_repository = MagicMock()
        mock_repository.create.side_effect = Exception("Database error")
        job_repository_factory = MagicMock(return_value=mock_repository)

        store_job_node = create_store_job_node(job_repository_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer"},
            "status": "in_progress",
            "cv_context": "Python developer",
            "is_relevant": True,
        }

        result = store_job_node(state)

        assert result["status"] == "error"

    def test_stores_job_without_extracted_skills(self):
        """Node stores job when extracted skills are not in state."""
        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        job_repository_factory = MagicMock(return_value=mock_repository)

        store_job_node = create_store_job_node(job_repository_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Python Developer",
                "description": "Some description",
            },
            "status": "in_progress",
            "cv_context": "Python developer",
            "is_relevant": True,
        }

        result = store_job_node(state)

        job_repository_factory.assert_called_once()
        mock_repository.create.assert_called_once()
        created_job = mock_repository.create.call_args[0][0]
        assert "must_have_skills" not in created_job
        assert "nice_to_have_skills" not in created_job
        assert result["status"] == "in_progress"

    def test_stores_job_with_empty_skills_lists(self):
        """Node stores job when extracted skills are empty lists."""
        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        job_repository_factory = MagicMock(return_value=mock_repository)

        store_job_node = create_store_job_node(job_repository_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Python Developer",
            },
            "status": "in_progress",
            "cv_context": "Python developer",
            "is_relevant": True,
            "extracted_must_have_skills": [],
            "extracted_nice_to_have_skills": [],
        }

        result = store_job_node(state)

        mock_repository.create.assert_called_once()
        created_job = mock_repository.create.call_args[0][0]
        # Empty lists are falsy, so skills shouldn't be added
        assert "must_have_skills" not in created_job
        assert "nice_to_have_skills" not in created_job
        assert result["status"] == "in_progress"

    def test_preserves_original_job_data(self):
        """Node preserves all original job fields when storing."""
        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        job_repository_factory = MagicMock(return_value=mock_repository)

        store_job_node = create_store_job_node(job_repository_factory)

        original_job = {
            "job_id": 1,
            "title": "Python Developer",
            "description": "Some description",
            "company": {"name": "TestCo"},
            "salary": {"min_value": 100000, "max_value": 150000},
        }

        state = {
            "job": original_job,
            "status": "in_progress",
            "cv_context": "Python developer",
            "is_relevant": True,
            "extracted_must_have_skills": ["Python"],
        }

        store_job_node(state)

        created_job = mock_repository.create.call_args[0][0]
        assert created_job["job_id"] == 1
        assert created_job["title"] == "Python Developer"
        assert created_job["description"] == "Some description"
        assert created_job["company"] == {"name": "TestCo"}
        assert created_job["salary"] == {"min_value": 100000, "max_value": 150000}

    def test_uses_default_status_when_missing_from_state(self):
        """Node uses 'in_progress' as default when status missing from state."""
        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        job_repository_factory = MagicMock(return_value=mock_repository)

        store_job_node = create_store_job_node(job_repository_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer"},
            "cv_context": "Python developer",
            "is_relevant": True,
        }

        result = store_job_node(state)

        assert result["status"] == "in_progress"
