"""Node identifiers for the job processing workflow."""

from enum import StrEnum


class JobProcessingNode(StrEnum):
    CHECK_JOB_RELEVANCE = "check_job_relevance"
    EXTRACT_MUST_HAVE_SKILLS = "extract_must_have_skills"
    EXTRACT_NICE_TO_HAVE_SKILLS = "extract_nice_to_have_skills"
    STORE_JOB = "store_job"
    PROCESS_JOBS = "process_jobs"
