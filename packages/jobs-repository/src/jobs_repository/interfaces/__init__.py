"""Interfaces for jobs repository services."""

from jobs_repository.interfaces.reference_data_service_interface import IReferenceDataService
from jobs_repository.interfaces.job_mapper_interface import IJobMapper

__all__ = [
    "IReferenceDataService",
    "IJobMapper",
]
