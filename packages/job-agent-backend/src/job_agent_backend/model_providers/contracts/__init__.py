"""Service-level contracts for model_providers.

This module contains interfaces that are used only within the model_providers service.
"""

from .provider_interface import IModelProvider
from .registry_interface import IModelRegistry

__all__ = [
    "IModelProvider",
    "IModelRegistry",
]
