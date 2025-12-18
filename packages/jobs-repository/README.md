# Jobs Repository

A PostgreSQL-based repository package for managing job listings and related data.

## Features

- PostgreSQL database connection management
- SQLAlchemy ORM for database operations
- Repository pattern for clean data access
- Alembic for database migrations

## Installation

```bash
pip install -e packages/jobs-repository
```

## Configuration

Set the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/dbname`)

## Usage

```python
from jobs_repository.database import get_db_session
from jobs_repository.repository import JobRepository

# Get database session
session = get_db_session()

# Create repository instance
job_repo = JobRepository(session)

# Use repository methods
jobs = job_repo.get_all()

# Get the most recent job timestamp (for search date auto-calculation)
latest_timestamp = job_repo.get_latest_updated_at()
```

## Repository Methods

| Method | Description |
|--------|-------------|
| `get_all()` | Retrieve all jobs from the database |
| `get_by_id(id)` | Retrieve a job by its ID |
| `save(job)` | Save a job to the database |
| `delete(id)` | Delete a job by its ID |
| `get_latest_updated_at()` | Get the most recent `updated_at` timestamp from all jobs, or `None` if no jobs exist |
