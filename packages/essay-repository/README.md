# Essay Repository

A PostgreSQL-based repository package for managing essay Q&A data with hybrid search support.

## Features

- PostgreSQL database connection management via `db-core`
- SQLAlchemy ORM for database operations
- Repository pattern with `BaseRepository` inheritance
- Hybrid search combining vector similarity and full-text search (pgvector + tsvector)
- Alembic for database migrations

## Installation

```bash
pip install -e packages/essay-repository
```

This package depends on `db-core` for shared database infrastructure.

## Configuration

Set the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/dbname`)

**Note:** The database must use the `pgvector/pgvector:pg16` image for vector search support.

## Usage

```python
from essay_repository import get_essay_repository, transaction

# Get repository instance via container
essay_repo = get_essay_repository()

# Create an essay
essay = essay_repo.create({
    "question": "What is your leadership experience?",
    "answer": "I led a team of 5 engineers..."
})

# Retrieve all essays
essays = essay_repo.get_all()

# Hybrid search (requires embedding vector)
results = essay_repo.search_hybrid(
    query="leadership",
    embedding=[0.1, 0.2, ...],  # 1536-dim vector
    limit=10,
    vector_weight=0.5
)

# Use transactions from db-core
with transaction() as session:
    essay_repo = get_essay_repository()
    essay_repo.create(essay_data)
```

Database utilities are re-exported from `db-core` for convenience:

```python
from essay_repository import (
    get_engine,
    get_session_factory,
    transaction,
    init_db,
)
```

## Repository Methods

| Method | Description |
|--------|-------------|
| `create(essay_data)` | Create a new essay |
| `get_by_id(id)` | Retrieve an essay by its ID |
| `get_all()` | Retrieve all essays |
| `update(id, essay_data)` | Update an existing essay |
| `delete(id)` | Delete an essay by its ID |
| `search_hybrid(query, embedding, limit, vector_weight)` | Hybrid vector + text search |
| `count()` | Get total number of essays |

## Architecture

`EssayRepository` inherits from `db_core.BaseRepository` and includes `EssaySearchMixin` for hybrid search, which provides:

- Session lifecycle management via `_session_scope()` context manager
- Support for both managed sessions (via session factory) and external sessions
- Consistent transaction handling with automatic commit/rollback
- Reciprocal Rank Fusion (RRF) for combining vector and text search results

The package maintains its own `Base` in `models/base.py` for Alembic migration isolation.

## Database Schema

The `essays` table includes:

- `id` - Primary key (UUID)
- `question` - Optional question text
- `answer` - Required answer text
- `keywords` - Optional keyword array
- `embedding` - Vector embedding (1536 dimensions for OpenAI)
- `search_vector` - Full-text search tsvector (auto-populated by trigger)
- `created_at`, `updated_at` - Timestamps

## Testing

```bash
cd packages/essay-repository
pytest
```

Tests are colocated alongside their corresponding modules (`*_test.py` naming convention).

## Development

- `pytest` to run the test suite
- `ruff format src/` for formatting
- `ruff check src/` for linting
