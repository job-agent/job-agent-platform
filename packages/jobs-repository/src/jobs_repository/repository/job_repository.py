"""Repository pattern implementation for job operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from jobs_repository.models import Job
from jobs_repository.schemas import JobCreate, JobUpdate, JobSearch
from jobs_repository.exceptions import (
    JobNotFoundError,
    JobAlreadyExistsError,
    TransactionError,
    ValidationError,
)


class JobRepository:
    """Repository for managing job database operations with improved error handling."""

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create(self, job_data: JobCreate | Dict[str, Any]) -> Job:
        """
        Create a new job entry with validation.

        Args:
            job_data: Job data as JobCreate schema or dictionary

        Returns:
            Created Job instance

        Raises:
            JobAlreadyExistsError: If job with external_id already exists
            ValidationError: If job data is invalid
            TransactionError: If database operation fails

        Example:
            >>> repo = JobRepository(session)
            >>> job = repo.create(JobCreate(
            ...     title="Software Engineer",
            ...     company="Tech Corp",
            ...     location="Remote"
            ... ))
        """
        try:
            # Convert to dict if Pydantic model
            if isinstance(job_data, JobCreate):
                data = job_data.model_dump(exclude_unset=True)
            else:
                data = job_data

            # Check for existing job with same external_id
            if "external_id" in data and data["external_id"]:
                existing = self.get_by_external_id(data["external_id"], data.get("source"))
                if existing:
                    raise JobAlreadyExistsError(data["external_id"], data.get("source", "unknown"))

            job = Job(**data)
            self.session.add(job)
            self.session.commit()
            self.session.refresh(job)
            return job

        except JobAlreadyExistsError:
            raise
        except IntegrityError as e:
            self.session.rollback()
            raise ValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            raise TransactionError(f"Failed to create job: {e}") from e

    def get_by_id(self, job_id: int) -> Optional[Job]:
        """
        Retrieve a job by its ID.

        Args:
            job_id: Job primary key

        Returns:
            Job instance or None if not found
        """
        try:
            return self.session.query(Job).filter(Job.id == job_id).first()
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to retrieve job: {e}") from e

    def get_by_id_or_raise(self, job_id: int) -> Job:
        """
        Retrieve a job by its ID or raise an error.

        Args:
            job_id: Job primary key

        Returns:
            Job instance

        Raises:
            JobNotFoundError: If job is not found
        """
        job = self.get_by_id(job_id)
        if not job:
            raise JobNotFoundError(job_id)
        return job

    def get_by_external_id(self, external_id: str, source: Optional[str] = None) -> Optional[Job]:
        """
        Retrieve a job by its external ID and optional source.

        Args:
            external_id: External job identifier
            source: Job source (e.g., "LinkedIn")

        Returns:
            Job instance or None if not found
        """
        try:
            query = self.session.query(Job).filter(Job.external_id == external_id)
            if source:
                query = query.filter(Job.source == source)
            return query.first()
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to retrieve job: {e}") from e

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> List[Job]:
        """
        Retrieve all jobs with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            order_by: Field to order by
            order_desc: Sort in descending order if True

        Returns:
            List of Job instances
        """
        try:
            search_params = JobSearch(
                is_active=is_active,
                skip=skip,
                limit=limit,
                order_by=order_by,
                order_desc=order_desc,
            )
            return self.search(search_params)
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to retrieve jobs: {e}") from e

    def search(
        self,
        search_params: Optional[JobSearch | Dict[str, Any]] = None,
        **kwargs,
    ) -> List[Job]:
        """
        Search jobs with multiple filters using JobSearch schema or kwargs.

        Args:
            search_params: JobSearch schema or dictionary with search parameters
            **kwargs: Alternative way to pass search parameters

        Returns:
            List of Job instances matching the criteria

        Example:
            >>> # Using JobSearch schema
            >>> results = repo.search(JobSearch(query_text="Python", is_remote=True))
            >>> # Using kwargs
            >>> results = repo.search(query_text="Python", is_remote=True)
        """
        try:
            # Build JobSearch instance
            if search_params is None:
                search = JobSearch(**kwargs)
            elif isinstance(search_params, JobSearch):
                # Merge with kwargs if provided
                if kwargs:
                    params = search_params.model_dump(exclude_unset=True)
                    params.update(kwargs)
                    search = JobSearch(**params)
                else:
                    search = search_params
            else:
                # Dict provided
                params = {**search_params, **kwargs}
                search = JobSearch(**params)

            # Build query with filters
            query = self.session.query(Job)
            query = search.apply_to_query(query, Job)

            # Apply ordering
            order_field = getattr(Job, search.order_by, Job.created_at)
            if search.order_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))

            # Apply pagination
            query = query.offset(search.skip).limit(search.limit)

            return query.all()
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to search jobs: {e}") from e

    def update(self, job_id: int, update_data: JobUpdate | Dict[str, Any]) -> Job:
        """
        Update a job entry with validation.

        Args:
            job_id: Job primary key
            update_data: JobUpdate schema or dictionary with fields to update

        Returns:
            Updated Job instance

        Raises:
            JobNotFoundError: If job is not found
            ValidationError: If update data is invalid
            TransactionError: If database operation fails
        """
        try:
            job = self.get_by_id_or_raise(job_id)

            # Convert to dict if Pydantic model
            if isinstance(update_data, JobUpdate):
                data = update_data.model_dump(exclude_unset=True)
            else:
                data = update_data

            for key, value in data.items():
                if hasattr(job, key):
                    setattr(job, key, value)

            job.updated_at = datetime.now(UTC)
            self.session.commit()
            self.session.refresh(job)
            return job

        except JobNotFoundError:
            raise
        except IntegrityError as e:
            self.session.rollback()
            raise ValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            raise TransactionError(f"Failed to update job: {e}") from e

    def delete(self, job_id: int) -> bool:
        """
        Delete a job entry (hard delete).

        Args:
            job_id: Job primary key

        Returns:
            True if deleted

        Raises:
            JobNotFoundError: If job is not found
            TransactionError: If database operation fails
        """
        try:
            job = self.get_by_id_or_raise(job_id)
            self.session.delete(job)
            self.session.commit()
            return True

        except JobNotFoundError:
            raise
        except SQLAlchemyError as e:
            self.session.rollback()
            raise TransactionError(f"Failed to delete job: {e}") from e

    def soft_delete(self, job_id: int) -> Job:
        """
        Soft delete a job by marking it as inactive.

        Args:
            job_id: Job primary key

        Returns:
            Updated Job instance

        Raises:
            JobNotFoundError: If job is not found
        """
        return self.update(job_id, {"is_active": False})

    def bulk_create(self, jobs_data: List[JobCreate | Dict[str, Any]]) -> List[Job]:
        """
        Create multiple job entries in a single transaction.

        Args:
            jobs_data: List of JobCreate schemas or dictionaries

        Returns:
            List of created Job instances

        Raises:
            ValidationError: If any job data is invalid
            TransactionError: If database operation fails
        """
        try:
            jobs = []
            for job_data in jobs_data:
                if isinstance(job_data, JobCreate):
                    data = job_data.model_dump(exclude_unset=True)
                else:
                    data = job_data
                jobs.append(Job(**data))

            self.session.add_all(jobs)
            self.session.commit()

            for job in jobs:
                self.session.refresh(job)

            return jobs

        except IntegrityError as e:
            self.session.rollback()
            raise ValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            raise TransactionError(f"Failed to bulk create jobs: {e}") from e

    def count(self, is_active: Optional[bool] = None, **filters) -> int:
        """
        Count total jobs with optional filters.

        Args:
            is_active: Filter by active status
            **filters: Additional filter parameters

        Returns:
            Total count of jobs
        """
        try:
            filter_params = {"is_active": is_active, "skip": 0, "limit": 1000, **filters}
            search = JobSearch(**filter_params)

            # Build query with filters (no pagination for count)
            query = self.session.query(Job)
            query = search.apply_to_query(query, Job)

            return query.count()
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to count jobs: {e}") from e

    def get_by_source(self, source: str, skip: int = 0, limit: int = 100) -> List[Job]:
        """
        Retrieve jobs from a specific source.

        Args:
            source: Job source identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Job instances from the source
        """
        try:
            return (
                self.session.query(Job)
                .filter(Job.source == source)
                .order_by(desc(Job.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to retrieve jobs by source: {e}") from e

    def upsert(self, external_id: str, source: str, job_data: JobCreate | Dict[str, Any]) -> Job:
        """
        Insert or update a job based on external_id and source.

        Args:
            external_id: External job identifier
            source: Job source
            job_data: JobCreate schema or dictionary with job data

        Returns:
            Created or updated Job instance

        Raises:
            ValidationError: If job data is invalid
            TransactionError: If database operation fails
        """
        try:
            existing_job = self.get_by_external_id(external_id, source)

            # Convert to dict if Pydantic model
            if isinstance(job_data, JobCreate):
                data = job_data.model_dump(exclude_unset=True)
            else:
                data = job_data.copy()

            if existing_job:
                # Update existing job
                for key, value in data.items():
                    if hasattr(existing_job, key) and key not in ["id", "created_at"]:
                        setattr(existing_job, key, value)
                existing_job.updated_at = datetime.now(UTC)
                self.session.commit()
                self.session.refresh(existing_job)
                return existing_job
            else:
                # Create new job
                data["external_id"] = external_id
                data["source"] = source
                return self.create(data)

        except IntegrityError as e:
            self.session.rollback()
            raise ValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            raise TransactionError(f"Failed to upsert job: {e}") from e

    def exists(self, job_id: int) -> bool:
        """
        Check if a job exists by ID.

        Args:
            job_id: Job primary key

        Returns:
            True if job exists, False otherwise
        """
        try:
            return self.session.query(Job.id).filter(Job.id == job_id).first() is not None
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to check job existence: {e}") from e

    def bulk_update_status(self, job_ids: List[int], is_active: bool) -> int:
        """
        Bulk update the active status of multiple jobs.

        Args:
            job_ids: List of job IDs to update
            is_active: New active status

        Returns:
            Number of jobs updated

        Raises:
            TransactionError: If database operation fails
        """
        try:
            result = (
                self.session.query(Job)
                .filter(Job.id.in_(job_ids))
                .update(
                    {"is_active": is_active, "updated_at": datetime.now(UTC)},
                    synchronize_session=False,
                )
            )
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise TransactionError(f"Failed to bulk update jobs: {e}") from e
