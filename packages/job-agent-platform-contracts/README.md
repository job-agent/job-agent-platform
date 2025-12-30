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
- `search_hybrid(query, embedding, limit, vector_weight)` - Hybrid search using vector and text

### ICVRepository

Interface for CV storage operations:

- `save(cv_content)` - Store CV content
- `find()` - Retrieve stored CV (returns `None` if not found)

### IJobAgentOrchestrator

Interface for the job processing pipeline orchestrator. Used by interfaces (Telegram bot, CLI) to interact with the backend.

## Data Models

- `JobProcessingResult` - Result of processing a single job
- `PipelineSummary` - Summary of a complete pipeline run
- `Essay`, `EssayCreate`, `EssayUpdate`, `EssaySearchResult` - Essay-related schemas

## Exceptions

The package exports a hierarchy of exceptions:

- `JobAgentError` - Base exception for all job-agent errors
- `RepositoryError` - Base for repository errors
- `JobAlreadyExistsError`, `JobNotFoundError` - Job-specific errors
- `EssayRepositoryError`, `EssayNotFoundError`, `EssayValidationError` - Essay-specific errors
- `ValidationError`, `TransactionError`, `DatabaseConnectionError` - General errors

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
