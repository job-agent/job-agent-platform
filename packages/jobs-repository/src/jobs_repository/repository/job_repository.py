"""Repository implementation focused on persisting job listings.

The module provides helper utilities to ensure reference entities (company, location,
category, industry) exist before a job is written, and exposes a small API for creating
jobs and looking them up by external identifier.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta, UTC
from typing import Callable, Generator, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, or_, func

from job_agent_platform_contracts import IJobRepository
from job_scrapper_contracts import JobDict
from jobs_repository.models import Job, Company
from jobs_repository.database.session import get_session_factory
from jobs_repository.interfaces import IReferenceDataService, IJobMapper
from job_agent_platform_contracts.job_repository.schemas import JobCreate
from job_agent_platform_contracts.job_repository.exceptions import (
    JobAlreadyExistsError,
    TransactionError,
    ValidationError,
)


class JobRepository(IJobRepository):
    """Repository that persists jobs and manages related reference data.

    The repository currently supports creating job records and fetching them by
    external identifier. Reference tables (companies, locations, categories,
    industries) are populated transparently through the helper methods.
    """

    def __init__(
        self,
        reference_data_service: IReferenceDataService,
        mapper: IJobMapper,
        session: Optional[Session] = None,
        session_factory: Optional[Callable[[], Session]] = None,
    ):
        """
        Initialize the repository with a managed or external session.

        Args:
            reference_data_service: Service for managing reference data entities
            mapper: Service for mapping between Job model and contract data
            session: Existing SQLAlchemy session to reuse
            session_factory: Callable returning SQLAlchemy session instances
        """
        if session is not None and session_factory is not None:
            raise ValueError("Provide either session or session_factory, not both")

        self.mapper = mapper
        self._reference_data_service = reference_data_service

        if session is not None:
            self._session_factory: Callable[[], Session] = lambda: session
            self._close_session = False
        else:
            factory_candidate = session_factory or get_session_factory()

            if not callable(factory_candidate):
                raise TypeError("session_factory must be callable")

            self._session_factory = lambda: factory_candidate()
            self._close_session = True

    @contextmanager
    def _session_scope(self, *, commit: bool) -> Generator[Session, None, None]:
        session = self._session_factory()
        close_session = self._close_session

        try:
            yield session
            if commit:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            if close_session:
                session.close()

    def _load_relationships(self, job: Job) -> None:
        if job.company_rel:
            _ = job.company_rel.name
        if job.location_rel:
            _ = job.location_rel.region
        if job.category_rel:
            _ = job.category_rel.name
        if job.industry_rel:
            _ = job.industry_rel.name

    def _get_job_by_external_id(
        self, session: Session, external_id: str, source: Optional[str]
    ) -> Optional[Job]:
        stmt = select(Job).where(Job.external_id == external_id)
        if source:
            stmt = stmt.where(Job.source == source)
        return session.scalar(stmt)

    def _get_job_by_source_url(
        self, session: Session, source_url: str, source: Optional[str]
    ) -> Optional[Job]:
        """Find job by source URL and optional source.

        Args:
            session: SQLAlchemy session
            source_url: The URL where the job was originally scraped from
            source: Optional job source (e.g., 'djinni', 'linkedin')

        Returns:
            Job instance if found, None otherwise
        """
        stmt = select(Job).where(Job.source_url == source_url)
        if source:
            stmt = stmt.where(Job.source == source)
        return session.scalar(stmt)

    def _find_existing_job(
        self, session: Session, external_id: str, source: Optional[str], source_url: Optional[str]
    ) -> Optional[Job]:
        """Check for existing job by external_id or source_url.

        Args:
            session: SQLAlchemy session
            external_id: External job identifier
            source: Optional job source (e.g., 'djinni', 'linkedin')
            source_url: Optional URL where the job was scraped from

        Returns:
            Job instance if found by either external_id or source_url, None otherwise
        """
        existing_job = self._get_job_by_external_id(session, external_id, source)

        if not existing_job and source_url:
            existing_job = self._get_job_by_source_url(session, source_url, source)

        return existing_job

    def _resolve_reference_data(self, session: Session, mapped_data: dict) -> None:
        """Resolve reference data entities and update mapped_data with foreign keys.

        Pops company_name, location_region, category_name, and industry_name from
        mapped_data and replaces them with their corresponding *_id fields.

        Args:
            session: SQLAlchemy session
            mapped_data: Mutable dictionary that will be modified in place
        """
        if company_name := mapped_data.pop("company_name", None):
            company = self._reference_data_service.get_or_create_company(session, company_name)
            mapped_data["company_id"] = company.id

        if location_region := mapped_data.pop("location_region", None):
            location = self._reference_data_service.get_or_create_location(session, location_region)
            mapped_data["location_id"] = location.id

        if category_name := mapped_data.pop("category_name", None):
            category = self._reference_data_service.get_or_create_category(session, category_name)
            mapped_data["category_id"] = category.id

        if industry_name := mapped_data.pop("industry_name", None):
            industry = self._reference_data_service.get_or_create_industry(session, industry_name)
            mapped_data["industry_id"] = industry.id

    def create(self, job_data: JobCreate) -> Job:
        """
        Create a new job from JobDict or JobCreate contract data.

        This method uses JobMapper to transform contract data to model format,
        then creates the job record with all related entities.

        Args:
            job_data: Job data in JobDict or JobCreate format from job-agent-platform-contracts.
                     JobCreate includes additional fields like must_have_skills
                     and nice_to_have_skills.

        Returns:
            Created Job instance

        Raises:
            JobAlreadyExistsError: If job with same external_id already exists
            ValidationError: If data validation fails
            TransactionError: If database transaction fails
        """
        try:
            with self._session_scope(commit=True) as session:
                mapped_data = self.mapper.map_to_model(job_data)

                self._resolve_reference_data(session, mapped_data)

                existing_job = self._find_existing_job(
                    session,
                    mapped_data["external_id"],
                    mapped_data.get("source"),
                    mapped_data.get("source_url"),
                )

                if existing_job:
                    raise JobAlreadyExistsError(
                        external_id=mapped_data["external_id"],
                        source=mapped_data.get("source") or "unknown",
                    )

                job = Job(**mapped_data)
                session.add(job)
                session.flush()
                session.refresh(job)
                self._load_relationships(job)
                if self._close_session:
                    session.expunge(job)
                return job

        except JobAlreadyExistsError:
            raise
        except IntegrityError as e:
            raise ValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to create job: {e}") from e

    def get_by_external_id(self, external_id: str, source: Optional[str] = None) -> Optional[Job]:
        """
        Get job by external ID and optional source.

        Args:
            external_id: External job identifier
            source: Optional job source (e.g., 'LinkedIn', 'Indeed')

        Returns:
            Job instance if found, None otherwise
        """
        with self._session_scope(commit=False) as session:
            stmt = select(Job).where(Job.external_id == external_id)
            if source:
                stmt = stmt.where(Job.source == source)
            job = session.scalar(stmt)
            if job:
                self._load_relationships(job)
                if self._close_session:
                    session.expunge(job)
            return job

    def has_active_job_with_title_and_company(self, title: str, company_name: str) -> bool:
        reference_time = datetime.now(UTC)
        expires_column = Job.__table__.c.expires_at
        if not getattr(expires_column.type, "timezone", False):
            reference_time = reference_time.replace(tzinfo=None)

        with self._session_scope(commit=False) as session:
            stmt = (
                select(Job.id)
                .join(Company)
                .where(Job.title == title)
                .where(Company.name == company_name)
                .where(or_(Job.expires_at.is_(None), Job.expires_at >= reference_time))
                .limit(1)
            )
            return session.scalar(stmt) is not None

    def get_existing_urls_by_source(self, source: str, days: Optional[int] = None) -> list[str]:
        """
        Get existing job URLs for a given source, optionally filtered by time window.

        Args:
            source: Job source (e.g., 'djinni', 'linkedin')
            days: Optional number of days to look back. If provided, only returns URLs
                  for jobs posted within the last N days. If None, returns all URLs.

        Returns:
            List of URLs for jobs from the specified source
        """
        with self._session_scope(commit=False) as session:
            stmt = select(Job.source_url).where(Job.source == source, Job.source_url.isnot(None))

            # Apply time-window filter if specified
            if days is not None:
                cutoff_date = datetime.now(UTC) - timedelta(days=days)

                # Handle timezone-aware vs timezone-naive comparison
                posted_at_column = Job.__table__.c.posted_at
                if not getattr(posted_at_column.type, "timezone", False):
                    cutoff_date = cutoff_date.replace(tzinfo=None)

                stmt = stmt.where(Job.posted_at >= cutoff_date)

            results = session.execute(stmt).scalars().all()
            return list(results)

    def save_filtered_jobs(self, jobs: List[JobDict]) -> int:
        """
        Save multiple filtered jobs in a batch operation.

        Filtered jobs are stored with is_filtered=True and is_relevant=False
        so they can be included in existing_urls for future scrapes.

        Args:
            jobs: List of job dictionaries that were rejected by pre-LLM filtering

        Returns:
            Count of jobs that were successfully saved (excluding duplicates)
        """
        if not jobs:
            return 0

        saved_count = 0
        with self._session_scope(commit=True) as session:
            for job_data in jobs:
                # Map job data to model format
                mapped_data = self.mapper.map_to_model(job_data)

                # Force filtered job flags
                mapped_data["is_filtered"] = True
                mapped_data["is_relevant"] = False

                existing_job = self._find_existing_job(
                    session,
                    mapped_data["external_id"],
                    mapped_data.get("source"),
                    mapped_data.get("source_url"),
                )

                if existing_job:
                    continue  # Skip duplicates

                self._resolve_reference_data(session, mapped_data)

                job = Job(**mapped_data)
                session.add(job)
                saved_count += 1

        return saved_count

    def get_latest_updated_at(self) -> Optional[datetime]:
        """
        Get the most recent updated_at timestamp from all jobs.

        This method is used to auto-calculate the search date range when
        the days parameter is not explicitly provided.

        Returns:
            The latest updated_at datetime if jobs exist, None otherwise.
        """
        with self._session_scope(commit=False) as session:
            stmt = select(func.max(Job.updated_at))
            result = session.scalar(stmt)
            return result
