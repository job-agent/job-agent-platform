"""Contracts module - Interfaces and abstractions for all services.

This module defines interfaces that other modules depend on, following the
Dependency Inversion Principle. Implementations should depend on these
abstractions rather than concrete implementations.
"""

from .scrapper import ScrapperServiceInterface

__all__ = ["ScrapperServiceInterface"]
__version__ = "0.1.0"
