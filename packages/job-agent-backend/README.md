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
├── src/
│   ├── data/
│   │   └── cvs/
│   └── job_agent_backend/
│       ├── container.py
│       ├── contracts/           # Package-level interfaces
│       ├── core/
│       ├── cv_loader/
│       ├── filter_service/
│       ├── messaging/
│       ├── model_providers/
│       │   └── contracts/       # Service-level interfaces
│       ├── services/
│       │   └── keyword_generation/  # LLM-based keyword extraction
│       └── workflows/
└── tests/
```

## Usage

```python
from job_agent_backend.core.orchestrator import JobAgentOrchestrator

orchestrator = JobAgentOrchestrator()
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

The dependency injection container exposed at `job_agent_backend.container.container` lets you override components such as the scrapper manager, repositories, or filter service when wiring the backend into other applications or tests.

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

### Essay Keyword Generation

When essays are created through `EssaySearchService`, keywords are automatically generated in the background using an LLM. The `KeywordGenerator` service extracts up to 10 keywords spanning hard skills, soft skills, and contextual labels:

```python
from job_agent_backend.container import get_essay_search_service
from job_agent_platform_contracts.essay_repository import EssayCreate

search_service = get_essay_search_service()

essay = search_service.create({
    "question": "Describe your leadership experience",
    "answer": "I led a team of 5 engineers to deliver a Python microservice..."
})
# Essay is returned immediately; keywords are generated asynchronously in a background thread
```

Keywords are only generated on essay creation, not on updates. The background generation uses the pre-configured `"keyword-extraction"` model (Ollama phi3:mini).

## Development

- `pytest` to run the test suite
- `ruff format src/` for formatting
- `ruff check src/` for linting
