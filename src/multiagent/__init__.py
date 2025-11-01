"""Multiagent system for job processing and PII removal.

This package provides workflows for:
- Job processing: relevance checking, skill extraction, and job analysis
- PII removal: cleaning personally identifiable information from CVs
"""

from .job_processing.agent import run_job_processing
from .pii_removal.agent import run_pii_removal

__all__ = [
    "run_job_processing",
    "run_pii_removal",
]
