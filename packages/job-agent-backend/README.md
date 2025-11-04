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
│       ├── contracts/
│       ├── core/
│       ├── cv_loader/
│       ├── filter_service/
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
    salary=5000,
    employment="remote",
)
print(summary)
```

The dependency injection container exposed at `job_agent_backend.container.container` lets you override components such as the scrapper manager, repositories, or filter service when wiring the backend into other applications or tests.

For lower-level access, the workflows can also be invoked directly:

```python
from job_agent_backend.workflows import run_job_processing, run_pii_removal

clean_cv = run_pii_removal(raw_cv_text)
result = run_job_processing(job_dict, clean_cv)
```

## Development

- `pytest` to run the test suite
- `black src/` for formatting
- `ruff check src/` for linting
