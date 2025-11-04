"""Filter service for job posts.

This service filters unsuitable job posts from the scrapper service
before passing them to the workflows system.
"""

from .filter import FilterService
from .filter_config import FilterConfig

__all__ = ["FilterService", "FilterConfig"]
__version__ = "0.1.0"
