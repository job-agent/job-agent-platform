"""Tests for CVRepository."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from cvs_repository import CVRepository


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cv_file_path(temp_dir):
    """Provide a CV file path in the temporary directory."""
    return temp_dir / "test_cv.txt"


@pytest.fixture
def repository(cv_file_path):
    """Provide a CVRepository instance."""
    return CVRepository(cv_file_path)


class TestCreate:
    """Tests for the create method."""

    def test_create_cv_in_non_existing_file(self, repository, cv_file_path):
        """Create CV in a file that doesn't exist yet."""
        cv_data = "John Doe\nSoftware Engineer\nExperience: 5 years"

        result = repository.create(cv_data)

        assert result == cv_data
        assert cv_file_path.exists()
        assert cv_file_path.read_text(encoding="utf-8") == cv_data

    def test_create_cv_with_parent_directory_creation(self, temp_dir):
        """Create CV when parent directory doesn't exist."""
        nested_path = temp_dir / "subdir1" / "subdir2" / "cv.txt"
        repository = CVRepository(nested_path)
        cv_data = "Test CV Content"

        result = repository.create(cv_data)

        assert result == cv_data
        assert nested_path.exists()
        assert nested_path.read_text(encoding="utf-8") == cv_data

    def test_create_empty_cv(self, repository, cv_file_path):
        """Create CV with empty content."""
        cv_data = ""

        result = repository.create(cv_data)

        assert result == ""
        assert cv_file_path.exists()
        assert cv_file_path.read_text(encoding="utf-8") == ""

    def test_create_cv_with_unicode_characters(self, repository, cv_file_path):
        """Create CV with Unicode characters."""
        cv_data = "Name: José García\nSkills: Python, JavaScript\nLocation: São Paulo 🇧🇷"

        result = repository.create(cv_data)

        assert result == cv_data
        assert cv_file_path.read_text(encoding="utf-8") == cv_data

    def test_create_overwrites_existing_cv(self, repository, cv_file_path):
        """Create CV overwrites existing file content."""
        initial_data = "Initial CV Content"
        new_data = "New CV Content"

        repository.create(initial_data)
        result = repository.create(new_data)

        assert result == new_data
        assert cv_file_path.read_text(encoding="utf-8") == new_data

    def test_create_with_large_content(self, repository, cv_file_path):
        """Create CV with large content."""
        cv_data = "Line of CV data\n" * 10000

        result = repository.create(cv_data)

        assert result == cv_data
        assert cv_file_path.read_text(encoding="utf-8") == cv_data

    def test_create_with_multiline_content(self, repository, cv_file_path):
        """Create CV with realistic multiline content."""
        cv_data = """John Doe
Software Engineer

EXPERIENCE:
- Company A (2020-2023): Senior Developer
- Company B (2018-2020): Developer

SKILLS:
- Python, Java, JavaScript
- Docker, Kubernetes
- AWS, GCP"""

        result = repository.create(cv_data)

        assert result == cv_data
        assert cv_file_path.read_text(encoding="utf-8") == cv_data


class TestFind:
    """Tests for the find method."""

    def test_find_existing_cv(self, repository, cv_file_path):
        """Find CV when file exists."""
        cv_data = "Test CV Content"
        cv_file_path.write_text(cv_data, encoding="utf-8")

        result = repository.find()

        assert result == cv_data

    def test_find_returns_none_when_file_not_exists(self, repository, cv_file_path):
        """Find returns None when CV file doesn't exist."""
        result = repository.find()

        assert result is None
        assert not cv_file_path.exists()

    def test_find_empty_cv(self, repository, cv_file_path):
        """Find CV with empty content."""
        cv_file_path.write_text("", encoding="utf-8")

        result = repository.find()

        assert result == ""

    def test_find_cv_with_unicode_characters(self, repository, cv_file_path):
        """Find CV with Unicode characters."""
        cv_data = "Name: 李明\nSkills: Python\nLocation: 北京 🇨🇳"
        cv_file_path.write_text(cv_data, encoding="utf-8")

        result = repository.find()

        assert result == cv_data

    def test_find_after_create(self, repository):
        """Find CV after creating it."""
        cv_data = "Created CV Content"

        repository.create(cv_data)
        result = repository.find()

        assert result == cv_data

    def test_find_with_special_characters(self, repository, cv_file_path):
        """Find CV with special characters and formatting."""
        cv_data = "Name: O'Brien\nEmail: user@example.com\nSalary: $100,000\nNotes: \"Excellent\" (top 10%)"
        cv_file_path.write_text(cv_data, encoding="utf-8")

        result = repository.find()

        assert result == cv_data


class TestUpdate:
    """Tests for the update method."""

    def test_update_existing_cv(self, repository, cv_file_path):
        """Update existing CV file."""
        initial_data = "Initial CV"
        updated_data = "Updated CV"
        cv_file_path.write_text(initial_data, encoding="utf-8")

        result = repository.update(updated_data)

        assert result == updated_data
        assert cv_file_path.read_text(encoding="utf-8") == updated_data

    def test_update_creates_file_if_not_exists(self, repository, cv_file_path):
        """Update creates file if it doesn't exist."""
        cv_data = "New CV via Update"

        result = repository.update(cv_data)

        assert result == cv_data
        assert cv_file_path.exists()
        assert cv_file_path.read_text(encoding="utf-8") == cv_data

    def test_update_with_empty_content(self, repository, cv_file_path):
        """Update CV with empty content."""
        cv_file_path.write_text("Original Content", encoding="utf-8")

        result = repository.update("")

        assert result == ""
        assert cv_file_path.read_text(encoding="utf-8") == ""

    def test_update_with_unicode_characters(self, repository, cv_file_path):
        """Update CV with Unicode characters."""
        initial_data = "Original CV"
        updated_data = "Updated: Müller, François, 中文"
        cv_file_path.write_text(initial_data, encoding="utf-8")

        result = repository.update(updated_data)

        assert result == updated_data
        assert cv_file_path.read_text(encoding="utf-8") == updated_data

    def test_update_after_create(self, repository):
        """Update CV after creating it."""
        initial_data = "Created CV"
        updated_data = "Updated CV"

        repository.create(initial_data)
        result = repository.update(updated_data)

        assert result == updated_data
        assert repository.find() == updated_data

    def test_multiple_sequential_updates(self, repository, cv_file_path):
        """Perform multiple sequential updates."""
        cv_file_path.write_text("Version 1", encoding="utf-8")

        repository.update("Version 2")
        repository.update("Version 3")
        result = repository.update("Version 4")

        assert result == "Version 4"
        assert cv_file_path.read_text(encoding="utf-8") == "Version 4"


class TestEdgeCases:
    """Tests for edge cases and various scenarios."""

    def test_repository_with_string_path(self, temp_dir):
        """Initialize repository with string path instead of Path object."""
        cv_file_path = str(temp_dir / "cv.txt")
        repository = CVRepository(cv_file_path)
        cv_data = "Test CV"

        result = repository.create(cv_data)

        assert result == cv_data
        assert Path(cv_file_path).exists()

    def test_repository_with_path_object(self, temp_dir):
        """Initialize repository with Path object."""
        cv_file_path = temp_dir / "cv.txt"
        repository = CVRepository(cv_file_path)
        cv_data = "Test CV"

        result = repository.create(cv_data)

        assert result == cv_data
        assert cv_file_path.exists()

    def test_file_path_is_converted_to_path_object(self, temp_dir):
        """Verify that file_path is stored as Path object."""
        cv_file_path = str(temp_dir / "cv.txt")
        repository = CVRepository(cv_file_path)

        assert isinstance(repository.file_path, Path)
        assert str(repository.file_path) == cv_file_path

    def test_create_find_update_workflow(self, repository):
        """Test complete workflow: create, find, update, find."""
        initial_cv = "Initial CV Data"
        updated_cv = "Updated CV Data"

        repository.create(initial_cv)
        found_cv = repository.find()
        assert found_cv == initial_cv

        repository.update(updated_cv)
        found_cv = repository.find()
        assert found_cv == updated_cv

    def test_find_on_readonly_file_succeeds(self, repository, cv_file_path):
        """Find succeeds on read-only file."""
        cv_data = "Read-only CV"
        cv_file_path.write_text(cv_data, encoding="utf-8")
        cv_file_path.chmod(0o444)

        try:
            result = repository.find()
            assert result == cv_data
        finally:
            cv_file_path.chmod(0o644)

    def test_create_fails_on_readonly_directory(self, temp_dir):
        """Create raises IOError when directory is read-only."""
        cv_file_path = temp_dir / "cv.txt"
        repository = CVRepository(cv_file_path)
        temp_dir.chmod(0o444)

        try:
            with pytest.raises(IOError):
                repository.create("Test CV")
        finally:
            temp_dir.chmod(0o755)

    def test_update_fails_on_readonly_file(self, repository, cv_file_path):
        """Update raises IOError when file is read-only."""
        cv_file_path.write_text("Original", encoding="utf-8")
        cv_file_path.chmod(0o444)

        try:
            with pytest.raises(IOError):
                repository.update("Updated")
        finally:
            cv_file_path.chmod(0o644)
