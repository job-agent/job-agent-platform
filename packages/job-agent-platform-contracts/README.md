# Contracts

Shared contracts and data models for the job-agent platform.

## Overview

This package contains shared data models, interfaces, and contracts used across different services in the job-agent platform.

## Key Interfaces

### IJobRepository

Interface for job persistence operations. Implementations must provide:

- `get_all()` - Retrieve all jobs
- `get_by_id(id)` - Retrieve job by ID
- `save(job)` - Persist a job
- `delete(id)` - Remove a job
- `get_latest_updated_at()` - Get the most recent `updated_at` timestamp from all stored jobs (returns `None` if no jobs exist)

### IEssayRepository

Interface for essay persistence operations. Implementations must provide:

**CRUD Operations:**
- `create(essay_data)` - Create a new essay
- `get_by_id(id)` - Retrieve essay by ID
- `get_all()` - Retrieve all essays
- `update(id, essay_data)` - Update an existing essay
- `delete(id)` - Remove an essay

## Installation

```bash
pip install -e .
```

## Development

Install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Testing

```bash
pytest
```
