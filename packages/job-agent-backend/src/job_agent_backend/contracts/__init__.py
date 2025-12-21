"""Package-level contracts for job-agent-backend.

This module contains interfaces that are used across multiple services within
job-agent-backend but not by other packages.
"""

from .cv_loader_interface import ICVLoader
from .filter_service_interface import IFilterService
from .model_factory_interface import IModelFactory
from .scrapper_client_interface import IScrapperClient

__all__ = [
    "ICVLoader",
    "IFilterService",
    "IModelFactory",
    "IScrapperClient",
]
