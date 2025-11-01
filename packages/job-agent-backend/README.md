# Job Agent Backend

The core backend service for the Job Agent platform, implementing a multi-agent system for job processing and filtering using LangGraph.

## Features

- **Multi-agent Workflows**: Orchestrated job processing workflows using LangGraph
- **Job Filtering**: Intelligent filtering service to match jobs with user criteria
- **PII Removal**: Workflow for removing personally identifiable information from CVs
- **Job Processing**: Complete pipeline for extracting and analyzing job requirements

## Installation

From the monorepo root:

```bash
pip install -e packages/job-agent-backend
```

Or with development dependencies:

```bash
pip install -e "packages/job-agent-backend[dev]"
```

## Structure

```
job-agent-backend/
├── src/
│   └── job_agent_backend/
│       ├── core/           # Core orchestration logic
│       ├── workflows/      # LangGraph workflows
│       ├── filter_service/ # Job filtering service
│       └── utils.py        # Utility functions
├── tests/                  # Unit tests
├── data/                   # Test data and resources
└── pyproject.toml         # Package configuration
```

## Dependencies

- LangGraph >= 1.0.2
- LangChain >= 1.0.3
- OpenAI >= 1.0.1
- Pydantic >= 2.0.0

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
ruff check src/
```
