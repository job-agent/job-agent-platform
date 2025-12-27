"""Test fixtures for filter service tests.

Note: sample_job_dict and sample_jobs_list fixtures are available from the
parent conftest.py at job_agent_backend level.
"""

from typing import Optional

import pytest


class StubJobRepository:
    """Configurable stub repository for filter service tests.

    This stub can be configured with:
    - external_ids: Set of job IDs that "exist" in the repository
    - active_pairs: Set of (title, company) pairs considered active
    - stored_jobs: Dict mapping external_id to job data (for more complex scenarios)
    """

    def __init__(
        self,
        external_ids: Optional[set] = None,
        active_pairs: Optional[set] = None,
        stored_jobs: Optional[dict] = None,
    ):
        self.external_ids = external_ids or set()
        self.active_pairs = active_pairs or set()
        self.stored_jobs = stored_jobs or {}

    def get_by_external_id(self, external_id, source=None):
        """Return job data if external_id exists in stored_jobs or external_ids."""
        if self.stored_jobs and str(external_id) in self.stored_jobs:
            return self.stored_jobs[str(external_id)]
        if str(external_id) in self.external_ids:
            return {"external_id": external_id}
        return None

    def has_active_job_with_title_and_company(self, title, company_name):
        """Return True if (title, company) pair is in active_pairs."""
        return (title, company_name) in self.active_pairs


class FailingJobRepository:
    """Repository stub that raises exceptions for testing error handling.

    Configure which method should fail:
    - fail_on_get_by_external_id: Raise on get_by_external_id calls
    - fail_on_has_active_job: Raise on has_active_job_with_title_and_company calls
    """

    def __init__(
        self,
        fail_on_get_by_external_id: bool = False,
        fail_on_has_active_job: bool = False,
        error_message: str = "Repository failure",
    ):
        self.fail_on_get_by_external_id = fail_on_get_by_external_id
        self.fail_on_has_active_job = fail_on_has_active_job
        self.error_message = error_message

    def get_by_external_id(self, external_id, source=None):
        if self.fail_on_get_by_external_id:
            raise RuntimeError(self.error_message)
        return None

    def has_active_job_with_title_and_company(self, title, company_name):
        if self.fail_on_has_active_job:
            raise RuntimeError(self.error_message)
        return False


@pytest.fixture
def stub_job_repository_factory():
    """Factory fixture for creating StubJobRepository instances.

    Usage:
        def test_example(stub_job_repository_factory):
            repo = stub_job_repository_factory(
                external_ids={"100", "200"},
                active_pairs={("Title", "Company")}
            )
            service = FilterService(job_repository_factory=lambda: repo)
    """

    def factory(
        external_ids: Optional[set] = None,
        active_pairs: Optional[set] = None,
        stored_jobs: Optional[dict] = None,
    ) -> StubJobRepository:
        return StubJobRepository(
            external_ids=external_ids,
            active_pairs=active_pairs,
            stored_jobs=stored_jobs,
        )

    return factory


@pytest.fixture
def failing_job_repository_factory():
    """Factory fixture for creating FailingJobRepository instances.

    Usage:
        def test_example(failing_job_repository_factory):
            repo = failing_job_repository_factory(
                fail_on_get_by_external_id=True,
                error_message="get_by_external_id failure"
            )
            service = FilterService(job_repository_factory=lambda: repo)
    """

    def factory(
        fail_on_get_by_external_id: bool = False,
        fail_on_has_active_job: bool = False,
        error_message: str = "Repository failure",
    ) -> FailingJobRepository:
        return FailingJobRepository(
            fail_on_get_by_external_id=fail_on_get_by_external_id,
            fail_on_has_active_job=fail_on_has_active_job,
            error_message=error_message,
        )

    return factory
