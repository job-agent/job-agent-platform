"""Tests for CVLoader implementation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from .loader import CVLoader


class TestLoadFromText:
    """Tests for CVLoader.load_from_text method."""

    def test_returns_content_for_valid_file(self, tmp_path: Path) -> None:
        cv_content = "Professional Experience:\n- 5 years Python development"
        cv_file = tmp_path / "cv.txt"
        cv_file.write_text(cv_content, encoding="utf-8")

        loader = CVLoader()
        result = loader.load_from_text(str(cv_file))

        assert result == cv_content

    def test_returns_none_for_nonexistent_file(self, tmp_path: Path) -> None:
        nonexistent_path = tmp_path / "nonexistent.txt"

        loader = CVLoader()
        result = loader.load_from_text(str(nonexistent_path))

        assert result is None

    def test_returns_none_on_read_error(self, tmp_path: Path) -> None:
        cv_file = tmp_path / "cv.txt"
        cv_file.write_bytes(b"\xff\xfe invalid utf-8 \x80\x81")

        loader = CVLoader()
        result = loader.load_from_text(str(cv_file))

        assert result is None


class TestLoadFromPdf:
    """Tests for CVLoader.load_from_pdf method."""

    def test_returns_extracted_content_for_valid_pdf(self, tmp_path: Path) -> None:
        pdf_file = tmp_path / "cv.pdf"
        pdf_file.touch()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Software Engineer with Python experience."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        loader = CVLoader()
        with patch("job_agent_backend.cv_loader.loader.PdfReader", return_value=mock_reader):
            result = loader.load_from_pdf(str(pdf_file))

        assert result == "Software Engineer with Python experience."

    def test_returns_none_for_nonexistent_pdf(self, tmp_path: Path) -> None:
        nonexistent_path = tmp_path / "nonexistent.pdf"

        loader = CVLoader()
        result = loader.load_from_pdf(str(nonexistent_path))

        assert result is None

    def test_returns_none_when_default_path_does_not_exist(self) -> None:
        loader = CVLoader()

        with patch.object(Path, "exists", return_value=False):
            result = loader.load_from_pdf(None)

        assert result is None

    def test_returns_none_on_pdf_read_error(self, tmp_path: Path) -> None:
        pdf_file = tmp_path / "corrupted.pdf"
        pdf_file.write_text("not a valid pdf content")

        loader = CVLoader()
        result = loader.load_from_pdf(str(pdf_file))

        assert result is None

    def test_returns_concatenated_content_from_multiple_pages(self, tmp_path: Path) -> None:
        pdf_file = tmp_path / "cv.pdf"
        pdf_file.touch()

        mock_page_1 = MagicMock()
        mock_page_1.extract_text.return_value = "Page 1 content."

        mock_page_2 = MagicMock()
        mock_page_2.extract_text.return_value = "Page 2 content."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page_1, mock_page_2]

        loader = CVLoader()
        with patch("job_agent_backend.cv_loader.loader.PdfReader", return_value=mock_reader):
            result = loader.load_from_pdf(str(pdf_file))

        assert result is not None
        assert "Page 1 content" in result
        assert "Page 2 content" in result
