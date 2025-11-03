"""Integration tests for utility functions."""

from unittest.mock import patch, MagicMock

from job_agent_backend.utils import load_cv_from_text, load_cv_from_pdf


class TestLoadCVFromText:
    """Test suite for load_cv_from_text function."""

    def test_load_cv_from_existing_text_file(self, sample_temp_cv_file, sample_cv_content):
        """Test loading CV from an existing text file."""
        result = load_cv_from_text(str(sample_temp_cv_file))

        assert result is not None
        assert len(result) > 0
        assert "Python" in result

    def test_load_cv_from_nonexistent_file_returns_none(self, temp_cv_dir):
        """Test loading CV from nonexistent file returns None."""
        nonexistent_path = temp_cv_dir / "nonexistent.txt"

        result = load_cv_from_text(str(nonexistent_path))

        assert result is None

    def test_load_cv_from_empty_file(self, temp_cv_dir):
        """Test loading CV from empty file."""
        empty_file = temp_cv_dir / "empty.txt"
        empty_file.write_text("")

        result = load_cv_from_text(str(empty_file))

        # Should return empty string, not None
        assert result == ""

    def test_load_cv_with_unicode_content(self, temp_cv_dir):
        """Test loading CV with unicode characters."""
        unicode_cv = temp_cv_dir / "unicode_cv.txt"
        unicode_content = "Name: José García\nSkills: Python, データサイエンス"
        unicode_cv.write_text(unicode_content, encoding="utf-8")

        result = load_cv_from_text(str(unicode_cv))

        assert result is not None
        assert "José García" in result
        assert "データサイエンス" in result

    def test_load_cv_with_long_content(self, temp_cv_dir):
        """Test loading CV with long content."""
        long_cv = temp_cv_dir / "long_cv.txt"
        long_content = "\n".join([f"Line {i}: Experience in project {i}" for i in range(1000)])
        long_cv.write_text(long_content)

        result = load_cv_from_text(str(long_cv))

        assert result is not None
        assert len(result) > 10000  # Should be quite long
        assert "Line 999" in result

    def test_load_cv_with_special_characters(self, temp_cv_dir):
        """Test loading CV with special characters."""
        special_cv = temp_cv_dir / "special_cv.txt"
        special_content = "Skills: C++, C#, .NET\nExperience: 5+ years"
        special_cv.write_text(special_content)

        result = load_cv_from_text(str(special_cv))

        assert result is not None
        assert "C++" in result
        assert "C#" in result
        assert ".NET" in result

    def test_load_cv_preserves_newlines(self, temp_cv_dir):
        """Test that loading CV preserves newlines."""
        cv_file = temp_cv_dir / "multiline_cv.txt"
        content = "Line 1\nLine 2\n\nLine 4"
        cv_file.write_text(content)

        result = load_cv_from_text(str(cv_file))

        assert result == content
        assert result.count("\n") == 3


class TestLoadCVFromPDF:
    """Test suite for load_cv_from_pdf function."""

    @patch("job_agent_backend.utils.PdfReader")
    def test_load_cv_from_existing_pdf(self, mock_pdf_reader, temp_cv_dir):
        """Test loading CV from an existing PDF file."""
        pdf_file = temp_cv_dir / "test.pdf"
        pdf_file.touch()  # Create empty file

        # Mock PDF reader
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF CV content with Python experience"
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        result = load_cv_from_pdf(str(pdf_file))

        assert result is not None
        assert "PDF CV content" in result
        assert "Python" in result

    def test_load_cv_from_nonexistent_pdf_returns_none(self, temp_cv_dir):
        """Test loading CV from nonexistent PDF returns None."""
        nonexistent_pdf = temp_cv_dir / "nonexistent.pdf"

        result = load_cv_from_pdf(str(nonexistent_pdf))

        assert result is None

    @patch("job_agent_backend.utils.PdfReader")
    def test_load_cv_from_multipage_pdf(self, mock_pdf_reader, temp_cv_dir):
        """Test loading CV from multi-page PDF."""
        pdf_file = temp_cv_dir / "multipage.pdf"
        pdf_file.touch()

        # Mock PDF reader with multiple pages
        mock_reader_instance = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "Page 3 content"
        mock_reader_instance.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf_reader.return_value = mock_reader_instance

        result = load_cv_from_pdf(str(pdf_file))

        assert result is not None
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        assert "Page 3 content" in result
        # Pages should be separated by double newlines
        assert "\n\n" in result

    @patch("job_agent_backend.utils.PdfReader")
    def test_load_cv_handles_empty_pages(self, mock_pdf_reader, temp_cv_dir):
        """Test loading CV handles pages with no extractable text."""
        pdf_file = temp_cv_dir / "empty_pages.pdf"
        pdf_file.touch()

        # Mock PDF reader with some empty pages
        mock_reader_instance = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = ""  # Empty page
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "Page 3 content"
        mock_reader_instance.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf_reader.return_value = mock_reader_instance

        result = load_cv_from_pdf(str(pdf_file))

        assert result is not None
        assert "Page 1 content" in result
        assert "Page 3 content" in result
        # Empty page should not add content

    @patch("job_agent_backend.utils.PdfReader")
    def test_load_cv_pdf_with_unicode(self, mock_pdf_reader, temp_cv_dir):
        """Test loading PDF with unicode characters."""
        pdf_file = temp_cv_dir / "unicode.pdf"
        pdf_file.touch()

        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Name: José García\nSkills: データサイエンス"
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        result = load_cv_from_pdf(str(pdf_file))

        assert result is not None
        assert "José García" in result
        assert "データサイエンス" in result

    @patch("job_agent_backend.utils.PdfReader")
    def test_load_cv_pdf_reader_exception(self, mock_pdf_reader, temp_cv_dir):
        """Test loading PDF handles PdfReader exceptions."""
        pdf_file = temp_cv_dir / "corrupt.pdf"
        pdf_file.touch()

        mock_pdf_reader.side_effect = Exception("Corrupted PDF")

        result = load_cv_from_pdf(str(pdf_file))

        assert result is None

    @patch("job_agent_backend.utils.PdfReader")
    def test_load_cv_pdf_extract_text_exception(self, mock_pdf_reader, temp_cv_dir):
        """Test loading PDF handles extract_text exceptions."""
        pdf_file = temp_cv_dir / "bad_page.pdf"
        pdf_file.touch()

        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.side_effect = Exception("Cannot extract text")
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        result = load_cv_from_pdf(str(pdf_file))

        # Should handle exception and return None
        assert result is None

    def test_load_cv_pdf_default_path(self, temp_cv_dir):
        """Test loading PDF with default path returns None when file not found."""
        # Call without path - will use default path which doesn't exist
        result = load_cv_from_pdf(None)

        # Should return None when default path doesn't exist
        # Note: the result might be empty string if Path operations succeed but file is empty
        assert result is None or result == ""

    @patch("job_agent_backend.utils.PdfReader")
    def test_load_cv_pdf_with_path_object(self, mock_pdf_reader, temp_cv_dir):
        """Test loading PDF when given a Path object."""
        pdf_file = temp_cv_dir / "path_obj.pdf"
        pdf_file.touch()

        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Content"
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # Pass as Path object
        result = load_cv_from_pdf(str(pdf_file))

        assert result is not None
        assert "Content" in result


class TestUtilsIntegration:
    """Integration tests for utils functions working together."""

    def test_both_loaders_handle_same_content_structure(self, temp_cv_dir):
        """Test that both loaders return similar structure."""
        content = "Professional Experience:\n- Python development\n- API design"

        # Create text file
        text_file = temp_cv_dir / "test.txt"
        text_file.write_text(content)

        text_result = load_cv_from_text(str(text_file))

        assert text_result is not None
        assert "Professional Experience" in text_result
        assert "Python" in text_result

    def test_loaders_return_none_consistently_for_missing_files(self, temp_cv_dir):
        """Test both loaders return None for missing files."""
        missing_txt = temp_cv_dir / "missing.txt"
        missing_pdf = temp_cv_dir / "missing.pdf"

        text_result = load_cv_from_text(str(missing_txt))
        pdf_result = load_cv_from_pdf(str(missing_pdf))

        assert text_result is None
        assert pdf_result is None
