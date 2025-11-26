"""Contracts package - interfaces have been moved to their respective implementation modules.

For backward compatibility, interfaces are re-exported here:
- ICVLoader: job_agent_backend.cv_loader.ICVLoader
- IScrapperClient: job_agent_backend.messaging.IScrapperClient
- IFilterService: job_agent_backend.filter_service.IFilterService
- IModelFactory: job_agent_backend.model_providers.interfaces.IModelFactory
"""

from job_agent_backend.cv_loader import ICVLoader
from job_agent_backend.filter_service import IFilterService
from job_agent_backend.messaging import IScrapperClient
from job_agent_backend.model_providers.interfaces import IModelFactory

__all__ = ["ICVLoader", "IFilterService", "IScrapperClient", "IModelFactory"]
