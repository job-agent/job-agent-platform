# Job Agent Backend

The backend package that powers the Job Agent platform. It orchestrates LangGraph workflows to sanitize candidate CVs, evaluate job relevance, and persist the most promising openings.

## Overview

This package bundles the orchestration logic, supporting services, and workflow entry points used by downstream interfaces such as the Telegram bot or any future API. It provides utilities for ingesting and storing CVs, scraping jobs through the shared scrapper service, filtering out unsuitable postings, and running LLM-backed workflows.

## Key Capabilities

- Multi-agent workflows implemented with LangGraph for PII removal and job processing.
- `JobAgentOrchestrator` integrates CV ingestion, job scraping, filtering, and persistence into a single pipeline.
- Dependency injection via `ApplicationContainer` so callers can swap repositories or services for testing and deployment.
- Configurable filter service with sensible defaults to suppress irrelevant jobs before invoking LLMs.
- CV loaders that handle PDF and text sources and persist sanitized content under `src/data/cvs`.

## Requirements

- Python 3.9 or newer
- `OPENAI_API_KEY` for the `langchain-openai` powered workflow nodes
- `DATABASE_URL` when persisting jobs through `jobs-repository`
- Access to the shared `scrapper-service` dependency (see that package for connection details)

## Installation

From the monorepo root:

```bash
pip install -e packages/job-agent-backend
```

With development dependencies:

```bash
pip install -e "packages/job-agent-backend[dev]"
```

## Package Layout

```
job-agent-backend/
├── pyproject.toml
├── README.md
└── src/
    ├── data/
    │   └── cvs/                 # Sanitized CV storage
    └── job_agent_backend/
        ├── container.py
        ├── contracts/           # Package-level interfaces
        ├── core/
        │   ├── orchestrator.py  # JobAgentOrchestrator - pipeline coordination
        │   └── cv_manager.py    # CVManager - CV storage and processing
        ├── cv_loader/
        ├── filter_service/
        ├── messaging/           # RabbitMQ client for scrapper communication
        ├── model_providers/
        │   └── contracts/       # Service-level interfaces
        ├── services/
        │   └── keyword_generation/  # LLM-based keyword extraction
        ├── utils/
        └── workflows/           # LangGraph workflows (PII removal, job processing)
```

Tests are colocated alongside their corresponding modules (`*_test.py` naming convention).

## Usage

Use the container's getter function to obtain a configured orchestrator instance:

```python
from job_agent_backend.container import get_orchestrator

orchestrator = get_orchestrator()
orchestrator.upload_cv(user_id=42, file_path="resume.pdf")
summary = orchestrator.run_complete_pipeline(
    user_id=42,
    min_salary=5000,
    employment_location="remote",
    days=7,  # Optional: search jobs from last N days
)
print(summary)
```

When `days` is omitted (or `None`), the orchestrator auto-calculates the date range based on the most recent job in the repository, capped at 5 days.

The dependency injection container exposed at `job_agent_backend.container.container` provides pre-configured instances. The container can also be used for testing by overriding providers.

Pre-configured AI models (e.g., `"skill-extraction"`, `"pii-removal"`, `"keyword-extraction"`, `"embedding"`) are registered in the container and can be accessed via:

```python
from job_agent_backend.container import get
from job_agent_backend.contracts import IModelFactory

factory = get(IModelFactory)
model = factory.get_model(model_id="skill-extraction")
```

For lower-level access, the workflows can also be invoked directly:

```python
from job_agent_backend.workflows import run_job_processing, run_pii_removal

clean_cv = run_pii_removal(raw_cv_text)
result = run_job_processing(job_dict, clean_cv)
```

### Essay Creation and Background Processing

When essays are created or updated through `EssaySearchService`, several background operations run asynchronously in daemon threads, allowing the methods to return immediately:

```python
from job_agent_backend.container import get_essay_search_service
from job_agent_platform_contracts.essay_repository import EssayCreate

search_service = get_essay_search_service()

essay = search_service.create({
    "question": "Describe your leadership experience",
    "answer": "I led a team of 5 engineers to deliver a Python microservice..."
})
# Essay is returned immediately; embedding and keywords are generated in background threads
```

**Background processing includes:**

- **Embedding generation** (create and update): Vector embeddings are generated asynchronously using the `"embedding"` model. Essays are immediately searchable via full-text search after creation; vector search becomes available once embedding generation completes.
- **Keyword generation** (create only): Up to 10 keywords (hard skills, soft skills, contextual labels) are extracted using the `"keyword-extraction"` model (Ollama phi3:mini).

Both processes handle failures gracefully: if embedding or keyword generation fails, the essay persists with NULL values for those fields, a warning is logged, and no exception propagates to the caller.

## Development

- `pytest` to run the test suite
- `ruff format src/` for formatting
- `ruff check src/` for linting
