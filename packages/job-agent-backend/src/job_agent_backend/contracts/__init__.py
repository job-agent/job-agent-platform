"""Service job-agent-platform-contracts for the job agent backend."""

from .cv_loader import ICVLoader
from .filter_service import IFilterService

__all__ = ["ICVLoader", "IFilterService"]
