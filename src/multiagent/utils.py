"""Utility functions for the multiagent system."""

import os
from pathlib import Path
from typing import Optional

from pypdf import PdfReader


def load_cv_from_pdf(cv_path: Optional[str] = None) -> Optional[str]:
    """
    Load CV content from a PDF file.

    Args:
        cv_path: Path to the CV PDF file. If not provided, defaults to
                 'data/cv.pdf' relative to the project root.

    Returns:
        The extracted text content from the PDF, or None if the file
        doesn't exist or cannot be read.

    Example:
        >>> cv_content = load_cv_from_pdf()
        >>> if cv_content:
        ...     print(f"Loaded CV with {len(cv_content)} characters")
    """
    # Default to data/cv.pdf in project root
    if cv_path is None:
        # Get project root (4 levels up from this file: utils.py -> multiagent -> src -> job-agent-platform)
        project_root = Path(__file__).parent.parent.parent
        cv_path = project_root / "data" / "cv.pdf"
    else:
        cv_path = Path(cv_path)

    # Check if file exists
    if not cv_path.exists():
        print(f"CV file not found at: {cv_path}")
        return None

    try:
        # Read PDF and extract text
        reader = PdfReader(cv_path)
        text_parts = []

        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text:
                text_parts.append(text)

        cv_content = "\n\n".join(text_parts)
        print(f"✓ Loaded CV from {cv_path} ({len(reader.pages)} pages, {len(cv_content)} characters)")
        return cv_content

    except Exception as e:
        print(f"Error reading CV PDF at {cv_path}: {e}")
        return None
