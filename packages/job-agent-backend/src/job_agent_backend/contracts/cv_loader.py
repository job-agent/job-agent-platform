"""CV loader contract definitions."""

from abc import ABC, abstractmethod
from typing import Optional


class ICVLoader(ABC):
    """Interface for components that provide CV loading capabilities."""

    @abstractmethod
    def load_from_text(self, cv_path: str) -> Optional[str]: ...

    @abstractmethod
    def load_from_pdf(self, cv_path: Optional[str] = None) -> Optional[str]: ...
