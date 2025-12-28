"""CV loader interface definitions."""

from typing import Optional, Protocol


class ICVLoader(Protocol):
    """Interface for components that provide CV loading capabilities."""

    def load_from_text(self, cv_path: str) -> Optional[str]: ...

    def load_from_pdf(self, cv_path: Optional[str] = None) -> Optional[str]: ...
