"""Utility class for the workflows system."""

import logging
import re
from pathlib import Path
from typing import Optional

from pypdf import PdfReader

from job_agent_backend.contracts import ICVLoader

logger = logging.getLogger(__name__)


class CVLoader(ICVLoader):
    """Utility class for loading CV content from various sources."""

    @staticmethod
    def _clean_pdf_text(text: str) -> str:
        """
        Clean up text extracted from PDF to fix formatting issues.

        Args:
            text: Raw text extracted from PDF

        Returns:
            Cleaned text with proper spacing and line breaks
        """
        # First, split into lines and remove whitespace-only lines
        lines = [line.strip() for line in text.split("\n")]
        lines = [line for line in lines if line]  # Remove empty lines

        if not lines:
            return ""

        # Join all non-empty lines into paragraphs
        # A new paragraph starts when a line ends with sentence-ending punctuation
        # followed by a line that starts with uppercase or special markers
        paragraphs = []
        current_paragraph = []

        for i, line in enumerate(lines):
            current_paragraph.append(line)

            # Check if this line ends a paragraph
            ends_sentence = line[-1] in ".!?"
            next_is_new_section = False

            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # New paragraph if next line starts with uppercase or common section markers
                next_is_new_section = next_line[0].isupper() and (
                    ends_sentence
                    or next_line.endswith(":")
                    or next_line.isupper()  # All caps (like headers)
                    or len(next_line.split()) <= 3
                )  # Short line (likely a header)

            if ends_sentence and (next_is_new_section or i == len(lines) - 1):
                # End current paragraph
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []

        # Add any remaining content as final paragraph
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        # Join paragraphs with double newlines
        result = "\n\n".join(paragraphs)

        # Clean up extra spaces
        result = re.sub(r" +", " ", result)

        return result.strip()

    def load_from_text(self, cv_path: str) -> Optional[str]:
        """
        Load CV content from a text file.

        Args:
            cv_path: Path to the CV text file.

        Returns:
            The CV content from the file, or None if the file
            doesn't exist or cannot be read.

        Example:
            >>> loader = CVLoader()
            >>> cv_content = loader.load_from_text('data/cvs/cv_12345.txt')
            >>> if cv_content:
            ...     print(f"Loaded CV with {len(cv_content)} characters")
        """
        cv_path_obj = Path(cv_path)
        if not cv_path_obj.exists():
            logger.warning("CV file not found at: %s", cv_path)
            return None

        try:
            cv_content = cv_path_obj.read_text(encoding="utf-8")
            logger.info("Loaded CV from %s (%d characters)", cv_path, len(cv_content))
            return cv_content
        except Exception as error:
            logger.error("Error reading CV text at %s: %s", cv_path, error)
            return None

    def load_from_pdf(self, cv_path: Optional[str] = None) -> Optional[str]:
        """
        Load CV content from a PDF file.

        Args:
            cv_path: Path to the CV PDF file. If not provided, the loader looks for
                'job_agent_backend/data/cv.pdf' relative to this package.

        Returns:
            The extracted text content from the PDF, or None if the file
            doesn't exist or cannot be read.

        Example:
            >>> loader = CVLoader()
            >>> cv_content = loader.load_from_pdf()
            >>> if cv_content:
            ...     print(f"Loaded CV with {len(cv_content)} characters")
        """
        target_path = self._resolve_pdf_path(cv_path)
        if not target_path.exists():
            logger.warning("CV file not found at: %s", target_path)
            return None

        try:
            reader = PdfReader(target_path)
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            raw_content = "\n\n".join(text_parts)
            cv_content = self._clean_pdf_text(raw_content)
            logger.info(
                "Loaded CV from %s (%d pages, %d characters)",
                target_path,
                len(reader.pages),
                len(cv_content),
            )
            return cv_content

        except Exception as error:
            logger.error("Error reading CV PDF at %s: %s", target_path, error)
            return None

    def _resolve_pdf_path(self, cv_path: Optional[str]) -> Path:
        if cv_path is not None:
            return Path(cv_path)
        project_root = Path(__file__).parent.parent
        return project_root / "data" / "cv.pdf"
