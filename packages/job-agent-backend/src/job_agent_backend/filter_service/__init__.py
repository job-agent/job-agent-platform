"""Filter service for job posts.

This service filters unsuitable job posts from the scrapper service
before passing them to the workflows system.
"""

from .filter import FilterService
from .filter_config import FilterConfig
from ..contracts.filter_service_interface import IFilterService

__all__ = ["FilterService", "FilterConfig", "IFilterService"]
__version__ = "0.1.0"
