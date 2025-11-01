"""Filter service for job posts.

This service filters unsuitable job posts from the scrapper service
before passing them to the workflows system.
"""

from .filter import FilterConfig, filter_jobs

__all__ = ["filter_jobs", "FilterConfig"]
__version__ = "0.1.0"
