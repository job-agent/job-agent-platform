# db-core

Shared database infrastructure for job-agent-platform repositories.

This package extracts common database utilities used by `jobs-repository` and `essay-repository`
to eliminate code duplication and ensure consistent database handling across the platform.

## Installation

```bash
pip install -e packages/db-core[dev]
```

Dependencies:
- `sqlalchemy>=2.0.0`
- `pydantic>=2.0.0`

## Quick Start

```python
from db_core import (
    get_engine,
    transaction,
    BaseRepository,
    DatabaseConnectionError,
    TransactionError,
)

# Use the transaction context manager
with transaction() as session:
    job = Job(title="Software Engineer")
    session.add(job)
# Auto-commits on success, rolls back on exception
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection URL |

Optional pool configuration can be set programmatically via `DatabaseConfig`.

## API Reference

### Configuration

**DatabaseConfig**

Pydantic model for database settings:

```python
from db_core import DatabaseConfig

# Reads DATABASE_URL from environment
config = DatabaseConfig()

# Or provide explicitly
config = DatabaseConfig(
    url="postgresql://user:pass@localhost:5432/db",
    pool_size=10,       # default: 10
    max_overflow=20,    # default: 20
    echo=False,         # default: False
)
```

**get_database_config()**

Factory function that creates `DatabaseConfig` from environment:

```python
from db_core import get_database_config

config = get_database_config()
print(config.url)
```

### Connection Management

**get_engine()**

Returns a thread-safe singleton SQLAlchemy engine:

```python
from db_core import get_engine

engine = get_engine()
# Engine is configured with pool_pre_ping for connection validation
# Verifies connectivity with SELECT 1 on first call
```

Raises `DatabaseConnectionError` if connection fails.

**reset_engine()**

Disposes the global engine (useful for testing):

```python
from db_core import reset_engine

reset_engine()  # Disposes connection pool
```

### Session Management

**get_session_factory()**

Returns a thread-safe singleton sessionmaker:

```python
from db_core import get_session_factory

SessionLocal = get_session_factory()
session = SessionLocal()
```

Sessions are configured with `autocommit=False` and `autoflush=False`.

**get_db_session()**

Generator that yields a managed session:

```python
from db_core import get_db_session

session = next(get_db_session())
try:
    # use session
    pass
finally:
    session.close()
```

Rolls back on `SQLAlchemyError`, always closes.

**transaction()**

Context manager for database transactions:

```python
from db_core import transaction

with transaction() as session:
    user = User(name="Alice")
    session.add(user)
# Commits on success, rolls back on exception
```

Raises `TransactionError` on failure.

### Lifecycle Functions

**init_db(base=None, engine=None)**

Creates all tables defined in the provided Base:

```python
from db_core import init_db, Base

# Using defaults
init_db()

# Using custom Base and engine
from mypackage.models import MyBase
init_db(base=MyBase, engine=my_engine)
```

For production, use Alembic migrations instead.

**drop_all_tables(base=None, engine=None)**

Drops all tables (use with caution):

```python
from db_core import drop_all_tables

drop_all_tables()  # Deletes all data
```

### Base Class

**Base**

SQLAlchemy declarative base for defining models:

```python
from db_core import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String)
```

Consumer packages can use this shared Base or define their own for Alembic isolation.

### Exceptions

**DatabaseError**

Base exception for all database-related errors.

**DatabaseConnectionError**

Raised when database connection fails (engine creation, SELECT 1 verification).

**TransactionError**

Raised when transaction operations fail (commit, rollback).

```python
from db_core import DatabaseConnectionError, TransactionError

try:
    with transaction() as session:
        session.add(entity)
except TransactionError as e:
    print(f"Transaction failed: {e}")
```

### BaseRepository

Abstract base class for repository implementations:

```python
from db_core import BaseRepository

class JobRepository(BaseRepository):
    def get_by_id(self, job_id: int):
        with self._session_scope(commit=False) as session:
            return session.query(Job).get(job_id)

    def save(self, job):
        with self._session_scope(commit=True) as session:
            session.add(job)
            session.flush()
            return job.id

# Using with session factory (managed sessions)
repo = JobRepository()

# Using with external session (shared transaction)
repo = JobRepository(session=existing_session)
```

Constructor parameters:
- `session`: Existing session to reuse (caller manages lifecycle)
- `session_factory`: Callable returning session instances

Provide one or the other, not both.

## Architecture Notes

### Consumer Packages

The following packages depend on db-core and inherit from `BaseRepository`:

- `jobs-repository` - Job listing persistence
- `essay-repository` - Essay Q&A persistence

Both packages re-export db-core utilities for convenience while maintaining
their own `Base` for Alembic migration isolation.

### Thread-Safe Singletons

Both `get_engine()` and `get_session_factory()` use double-checked locking
to ensure thread-safe singleton initialization.

### Global State

When multiple packages use db-core with the same `DATABASE_URL`, they share
the same engine and session factory. This is intentional for packages
operating on the same database.

### Alembic Compatibility

Each repository package maintains its own `Base` in `models/base.py` for Alembic migrations.
This ensures migration isolation between packages while sharing the underlying
database infrastructure.

## Testing

```bash
cd packages/db-core
pytest src/db_core/
```

For tests, use `reset_engine()` and `reset_session_factory()` in fixtures
to ensure test isolation.
