"""Repository pattern implementation for job operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from jobs_repository.models import Job


class JobRepository:
    """Repository for managing job database operations."""

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create(self, job_data: Dict[str, Any]) -> Job:
        """
        Create a new job entry.

        Args:
            job_data: Dictionary containing job data

        Returns:
            Created Job instance

        Example:
            >>> repo = JobRepository(session)
            >>> job = repo.create({
            ...     "title": "Software Engineer",
            ...     "company": "Tech Corp",
            ...     "location": "Remote"
            ... })
        """
        job = Job(**job_data)
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get_by_id(self, job_id: int) -> Optional[Job]:
        """
        Retrieve a job by its ID.

        Args:
            job_id: Job primary key

        Returns:
            Job instance or None if not found
        """
        return self.session.query(Job).filter(Job.id == job_id).first()

    def get_by_external_id(self, external_id: str, source: Optional[str] = None) -> Optional[Job]:
        """
        Retrieve a job by its external ID and optional source.

        Args:
            external_id: External job identifier
            source: Job source (e.g., "LinkedIn")

        Returns:
            Job instance or None if not found
        """
        query = self.session.query(Job).filter(Job.external_id == external_id)
        if source:
            query = query.filter(Job.source == source)
        return query.first()

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
        query = self.session.query(Job)

        if is_active is not None:
            query = query.filter(Job.is_active == is_active)

        # Apply ordering
        order_field = getattr(Job, order_by, Job.created_at)
        if order_desc:
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))

        return query.offset(skip).limit(limit).all()

    def search(
        self,
        query_text: Optional[str] = None,
        company: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        is_remote: Optional[bool] = None,
        is_active: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Job]:
        """
        Search jobs with multiple filters.

        Args:
            query_text: Search text for title or description
            company: Filter by company name
            location: Filter by location
            job_type: Filter by job type
            is_remote: Filter by remote status
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Job instances matching the criteria
        """
        query = self.session.query(Job)

        # Build filters
        filters = []

        if is_active is not None:
            filters.append(Job.is_active == is_active)

        if query_text:
            text_filter = or_(
                Job.title.ilike(f"%{query_text}%"),
                Job.description.ilike(f"%{query_text}%"),
            )
            filters.append(text_filter)

        if company:
            filters.append(Job.company.ilike(f"%{company}%"))

        if location:
            filters.append(Job.location.ilike(f"%{location}%"))

        if job_type:
            filters.append(Job.job_type == job_type)

        if is_remote is not None:
            filters.append(Job.is_remote == is_remote)

        if filters:
            query = query.filter(and_(*filters))

        return query.order_by(desc(Job.created_at)).offset(skip).limit(limit).all()

    def update(self, job_id: int, update_data: Dict[str, Any]) -> Optional[Job]:
        """
        Update a job entry.

        Args:
            job_id: Job primary key
            update_data: Dictionary containing fields to update

        Returns:
            Updated Job instance or None if not found
        """
        job = self.get_by_id(job_id)
        if not job:
            return None

        for key, value in update_data.items():
            if hasattr(job, key):
                setattr(job, key, value)

        job.updated_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(job)
        return job

    def delete(self, job_id: int) -> bool:
        """
        Delete a job entry (hard delete).

        Args:
            job_id: Job primary key

        Returns:
            True if deleted, False if not found
        """
        job = self.get_by_id(job_id)
        if not job:
            return False

        self.session.delete(job)
        self.session.commit()
        return True

    def soft_delete(self, job_id: int) -> Optional[Job]:
        """
        Soft delete a job by marking it as inactive.

        Args:
            job_id: Job primary key

        Returns:
            Updated Job instance or None if not found
        """
        return self.update(job_id, {"is_active": False})

    def bulk_create(self, jobs_data: List[Dict[str, Any]]) -> List[Job]:
        """
        Create multiple job entries in a single transaction.

        Args:
            jobs_data: List of dictionaries containing job data

        Returns:
            List of created Job instances
        """
        jobs = [Job(**job_data) for job_data in jobs_data]
        self.session.add_all(jobs)
        self.session.commit()

        for job in jobs:
            self.session.refresh(job)

        return jobs

    def count(self, is_active: Optional[bool] = None) -> int:
        """
        Count total jobs with optional active filter.

        Args:
            is_active: Filter by active status

        Returns:
            Total count of jobs
        """
        query = self.session.query(Job)
        if is_active is not None:
            query = query.filter(Job.is_active == is_active)
        return query.count()

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
        return (
            self.session.query(Job)
            .filter(Job.source == source)
            .order_by(desc(Job.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def upsert(self, external_id: str, source: str, job_data: Dict[str, Any]) -> Job:
        """
        Insert or update a job based on external_id and source.

        Args:
            external_id: External job identifier
            source: Job source
            job_data: Dictionary containing job data

        Returns:
            Created or updated Job instance
        """
        existing_job = self.get_by_external_id(external_id, source)

        if existing_job:
            # Update existing job
            for key, value in job_data.items():
                if hasattr(existing_job, key):
                    setattr(existing_job, key, value)
            existing_job.updated_at = datetime.now(UTC)
            self.session.commit()
            self.session.refresh(existing_job)
            return existing_job
        else:
            # Create new job
            job_data["external_id"] = external_id
            job_data["source"] = source
            return self.create(job_data)
