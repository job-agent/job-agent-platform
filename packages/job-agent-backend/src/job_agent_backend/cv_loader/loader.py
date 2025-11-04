"""Utility class for the workflows system."""

from pathlib import Path
from typing import Optional

from pypdf import PdfReader


class CVLoader:
    """Utility class for loading CV content from various sources."""

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
            print(f"CV file not found at: {cv_path}")
            return None

        try:
            cv_content = cv_path_obj.read_text(encoding="utf-8")
            print(f"✓ Loaded CV from {cv_path} ({len(cv_content)} characters)")
            return cv_content
        except Exception as error:
            print(f"Error reading CV text at {cv_path}: {error}")
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
            print(f"CV file not found at: {target_path}")
            return None

        try:
            reader = PdfReader(target_path)
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            cv_content = "\n\n".join(text_parts)
            print(
                f"✓ Loaded CV from {target_path} ({len(reader.pages)} pages, {len(cv_content)} characters)"
            )
            return cv_content

        except Exception as error:
            print(f"Error reading CV PDF at {target_path}: {error}")
            return None

    def _resolve_pdf_path(self, cv_path: Optional[str]) -> Path:
        if cv_path is not None:
            return Path(cv_path)
        project_root = Path(__file__).parent.parent
        return project_root / "data" / "cv.pdf"
