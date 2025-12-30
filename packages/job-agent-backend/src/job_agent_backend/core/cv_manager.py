"""CV management functionality for job processing.

This module provides the CVManager class that handles CV-related operations
including storage path management, upload processing, and content retrieval.
"""

from pathlib import Path
from typing import Callable, Optional

from job_agent_platform_contracts import ICVRepository
from job_agent_backend.cv_loader import ICVLoader


CVRepositoryFactory = Callable[[str | Path], ICVRepository]
PIIRemovalFunc = Callable[[str], str]


class CVManager:
    """Manages CV storage, upload processing, and retrieval.

    This class encapsulates all CV-related operations, including:
    - Path management for user CVs
    - Upload processing (PDF/text extraction, PII removal)
    - CV content retrieval
    """

    def __init__(
        self,
        cv_repository_class: CVRepositoryFactory,
        cv_loader: ICVLoader,
        pii_removal_func: PIIRemovalFunc,
        logger: Optional[Callable[[str], None]] = None,
    ):
        """Initialize the CV manager.

        Args:
            cv_repository_class: Factory for creating CV repository instances.
            cv_loader: Loader implementation for reading CV content.
            pii_removal_func: Function to remove PII from CV content.
            logger: Optional logging function to report progress.
                   If None, will use print().
        """
        self.logger: Callable[[str], None] = logger or print
        self.cv_repository_class: CVRepositoryFactory = cv_repository_class
        self.cv_loader: ICVLoader = cv_loader
        self._pii_removal_func: PIIRemovalFunc = pii_removal_func

    def get_cv_path(self, user_id: int) -> Path:
        """Get the storage path for a user's CV.

        Args:
            user_id: User identifier (e.g., Telegram user ID)

        Returns:
            Path object for the user's CV file
        """
        package_root = Path(__file__).parent.parent.parent
        cv_dir = package_root / "data" / "cvs"
        cv_dir.mkdir(parents=True, exist_ok=True)
        return cv_dir / f"cv_{user_id}.txt"

    def upload_cv(self, user_id: int, file_path: str) -> None:
        """Upload and process a CV file for a user.

        Automatically detects file type and processes accordingly.
        Supports PDF and text files.

        Args:
            user_id: User identifier
            file_path: Path to CV file (PDF or text)

        Raises:
            ValueError: If file format is unsupported or processing fails
        """
        file_path_lower = file_path.lower()

        if file_path_lower.endswith(".pdf"):
            self.logger(f"Processing PDF CV for user {user_id}")
            cv_content = self.cv_loader.load_from_pdf(file_path)
        elif file_path_lower.endswith(".txt"):
            self.logger(f"Processing text CV for user {user_id}")
            cv_content = self.cv_loader.load_from_text(file_path)
        else:
            extension = Path(file_path).suffix
            raise ValueError(f"Unsupported file format: {extension}. Supported formats: .pdf, .txt")

        if not cv_content:
            raise ValueError("Failed to extract content from CV file")

        self.logger(f"Removing PII from CV for user {user_id}")
        cleaned_cv_content = self._pii_removal_func(cv_content)
        self.logger(f"PII removed from CV for user {user_id}")

        cv_path = self.get_cv_path(user_id)
        cv_repository = self.cv_repository_class(cv_path)
        cv_repository.create(cleaned_cv_content)
        self.logger(f"CV saved for user {user_id}")

    def has_cv(self, user_id: int) -> bool:
        """Check if a user has uploaded a CV.

        Args:
            user_id: User identifier

        Returns:
            True if user has a CV, False otherwise
        """
        try:
            cv_path = self.get_cv_path(user_id)
            cv_repository = self.cv_repository_class(cv_path)
            return cv_repository.find() is not None
        except Exception:
            return False

    def load_cv(self, user_id: int) -> str:
        """Load CV content for a user from repository.

        The CV is already cleaned of PII (done during upload).

        Args:
            user_id: User identifier

        Returns:
            CV content (already cleaned of PII)

        Raises:
            ValueError: If CV is not found or cannot be loaded
        """
        self.logger(f"Loading CV from repository for user {user_id}")
        cv_path = self.get_cv_path(user_id)
        cv_repository = self.cv_repository_class(cv_path)
        cv_content = cv_repository.find()

        if not cv_content:
            raise ValueError(f"CV not found for user {user_id}. Please upload a CV first.")

        self.logger(f"CV loaded successfully for user {user_id}")
        return cv_content
