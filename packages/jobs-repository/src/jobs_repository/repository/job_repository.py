"""Repository pattern implementation for job operations.

This repository follows a single-repository pattern where the Job entity is the primary
concern, and reference entities (Company, Location, Category, Industry) are managed as
supporting data that gets created automatically when storing jobs.

Structure:
    - Internal Helper Methods: get_or_create_* for reference data (companies, locations, etc.)
    - Core CRUD Operations: create, get, update, delete operations
    - Query & Search Methods: Specialized queries for finding jobs
    - Bulk Operations: Efficient multi-record operations
    - Utility Methods: Helper functions for common tasks
"""

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select

from job_agent_platform_contracts import IJobRepository
from jobs_repository.models import Job, Company, Location, Category, Industry
from jobs_repository.mapper import JobMapper
from job_agent_platform_contracts.job_repository.schemas import JobCreate
from job_agent_platform_contracts.job_repository.exceptions import (
    JobAlreadyExistsError,
    TransactionError,
    ValidationError,
)


class JobRepository(IJobRepository):
    """
    Repository for managing job database operations.

    This repository manages all job-related database operations including creating,
    retrieving, updating, and deleting jobs. Reference entities (companies, locations,
    categories, industries) are managed internally through get_or_create methods.

    All job data flows through this single repository, ensuring consistency and
    simplifying the API for consumers.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.mapper = JobMapper()

    def _get_or_create_company(self, name: str) -> Company:
        """
        Get existing company or create new one.

        Args:
            name: Company name

        Returns:
            Company instance
        """
        stmt = select(Company).where(Company.name == name)
        company = self.session.scalar(stmt)

        if company:
            return company

        company = Company(name=name)
        self.session.add(company)
        self.session.flush()
        return company

    def _get_or_create_location(self, region: str) -> Location:
        """
        Get existing location or create new one.

        Args:
            region: Location region/name

        Returns:
            Location instance
        """
        stmt = select(Location).where(Location.region == region)
        location = self.session.scalar(stmt)

        if location:
            return location

        location = Location(region=region)
        self.session.add(location)
        self.session.flush()
        return location

    def _get_or_create_category(self, name: str) -> Category:
        """
        Get existing category or create new one.

        Args:
            name: Category name

        Returns:
            Category instance
        """
        stmt = select(Category).where(Category.name == name)
        category = self.session.scalar(stmt)

        if category:
            return category

        category = Category(name=name)
        self.session.add(category)
        self.session.flush()
        return category

    def _get_or_create_industry(self, name: str) -> Industry:
        """
        Get existing industry or create new one.

        Args:
            name: Industry name

        Returns:
            Industry instance
        """
        stmt = select(Industry).where(Industry.name == name)
        industry = self.session.scalar(stmt)

        if industry:
            return industry

        industry = Industry(name=name)
        self.session.add(industry)
        self.session.flush()
        return industry

    def create(self, job_data: JobCreate) -> Job:
        """
        Create a new job from JobDict or JobCreate contract data.

        This method uses JobMapper to transform contract data to model format,
        then creates the job record with all related entities.

        Args:
            job_data: Job data in JobDict or JobCreate format from contracts.
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
            mapped_data = self.mapper.map_to_model(job_data)

            if company_name := mapped_data.pop("company_name", None):
                company = self._get_or_create_company(company_name)
                mapped_data["company_id"] = company.id

            if location_region := mapped_data.pop("location_region", None):
                location = self._get_or_create_location(location_region)
                mapped_data["location_id"] = location.id

            if category_name := mapped_data.pop("category_name", None):
                category = self._get_or_create_category(category_name)
                mapped_data["category_id"] = category.id

            if industry_name := mapped_data.pop("industry_name", None):
                industry = self._get_or_create_industry(industry_name)
                mapped_data["industry_id"] = industry.id

            existing_job = self.get_by_external_id(
                mapped_data["external_id"], mapped_data.get("source")
            )
            if existing_job:
                self.session.rollback()
                raise JobAlreadyExistsError(
                    external_id=mapped_data["external_id"],
                    source=mapped_data.get("source", "unknown"),
                )

            job = Job(**mapped_data)
            self.session.add(job)
            self.session.commit()
            self.session.refresh(job)
            return job

        except JobAlreadyExistsError:
            self.session.rollback()
            raise
        except IntegrityError as e:
            self.session.rollback()
            raise ValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            self.session.rollback()
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
        stmt = select(Job).where(Job.external_id == external_id)
        if source:
            stmt = stmt.where(Job.source == source)
        return self.session.scalar(stmt)
