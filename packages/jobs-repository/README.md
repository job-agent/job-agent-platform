# Jobs Repository

A PostgreSQL-based repository package for managing job listings and related data.

## Features

- PostgreSQL database connection management via `db-core`
- SQLAlchemy ORM for database operations
- Repository pattern with `BaseRepository` inheritance
- Alembic for database migrations

## Installation

```bash
pip install -e packages/jobs-repository
```

This package depends on `db-core` for shared database infrastructure.

## Configuration

Set the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/dbname`)

## Usage

```python
from jobs_repository import get_job_repository, transaction

# Get repository instance via container
job_repo = get_job_repository()

# Use repository methods
jobs = job_repo.get_all()

# Get the most recent job timestamp (for search date auto-calculation)
latest_timestamp = job_repo.get_latest_updated_at()

# Use transactions from db-core
with transaction() as session:
    job_repo = get_job_repository()
    job_repo.save(job_data)
```

Database utilities are re-exported from `db-core` for convenience:

```python
from jobs_repository import (
    get_engine,
    get_session_factory,
    transaction,
    init_db,
)
```

## Repository Methods

| Method | Description |
|--------|-------------|
| `get_all()` | Retrieve all jobs from the database |
| `get_by_id(id)` | Retrieve a job by its ID |
| `save(job)` | Save a job to the database |
| `delete(id)` | Delete a job by its ID |
| `get_latest_updated_at()` | Get the most recent `updated_at` timestamp from all jobs, or `None` if no jobs exist |

## Architecture

`JobRepository` inherits from `db_core.BaseRepository`, which provides:

- Session lifecycle management via `_session_scope()` context manager
- Support for both managed sessions (via session factory) and external sessions
- Consistent transaction handling with automatic commit/rollback

The package maintains its own `Base` in `models/base.py` for Alembic migration isolation.
