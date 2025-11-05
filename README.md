# Job Agent Platform

## How to Set Up

1. Create and activate a Python 3.9+ virtual environment.
2. Rename `.env.example` (if present) to `.env` in the repository root.
3. Populate the `.env` file with the environment variables described below.
4. Decide how to satisfy the `scrapper-service` dependency in `packages/job-agent-backend/pyproject.toml`. You can either point the entry to your own implementation or switch to the provided mock when the private repository is unavailable:

   ```toml
   # Example: comment the private dependency and enable the mock implementation
   # "scrapper-service @ git+ssh://git@github.com/job-agent/scrappers.git@v0.1.3#subdirectory=packages/scrapper-service"
   "scrapper-service @ git+ssh://git@github.com/job-agent/scrappers-mock.git@v0.1.0#subdirectory=packages/scrapper-service"
   ```

5. Install project packages in editable mode:

   ```bash
   pip install -e packages/jobs-repository
   pip install -e packages/cvs-repository
   pip install -e packages/job-agent-backend
   pip install -e packages/telegram_bot
   ```

6. Optional: install development extras when running tests or tooling:

   ```bash
   pip install -e "packages/jobs-repository[dev]"
   pip install -e "packages/cvs-repository[dev]"
   pip install -e "packages/job-agent-backend[dev]"
   pip install -e "packages/telegram_bot[dev]"
   ```

7. Apply database migrations if you plan to persist jobs:

   ```bash
   cd packages/jobs-repository
   alembic upgrade head
   ```

8. Start the Telegram bot with either `python -m telegram_bot.main` or `docker compose up` from the repository root.

### Required Environment Variables

- `OPENAI_API_KEY` — enables LangGraph workflows that rely on OpenAI models.
- `TELEGRAM_BOT_TOKEN` — token issued by @BotFather so the bot can connect to Telegram.
- `DATABASE_URL` — PostgreSQL connection string used by `jobs-repository` for persistence.
- `POSTGRES_USER` — PostgreSQL username used by `jobs-repository` connections.
- `POSTGRES_PASSWORD` — password paired with `POSTGRES_USER` for database access.
- `POSTGRES_DB` — database name that `jobs-repository` connects to.
- `POSTGRES_PORT` — network port where PostgreSQL accepts connections.
- `LANGSMITH_API_KEY` (optional) — enables LangSmith tracing and analytics for LangGraph runs.
- `LANGSMITH_TRACING_V2` and `LANGSMITH_PROJECT` (optional) — configure tracing behavior when LangSmith is enabled.
- Scrapper service credentials (if applicable) — match the configuration expected by the dependency injector when contacting the job scrapper service.

### About `scrapper-service`

`packages/job-agent-backend/pyproject.toml` pins a private dependency:

```toml
"scrapper-service @ git+ssh://git@github.com/job-agent/scrappers.git@v0.1.3#subdirectory=packages/scrapper-service"
```

If you do not have access to that repository, either point the dependency to your own compatible scrapper implementation or comment out the private line and enable the provided mock entry:

```toml
# "scrapper-service @ git+ssh://git@github.com/job-agent/scrappers.git@v0.1.3#subdirectory=packages/scrapper-service"
"scrapper-service @ git+ssh://git@github.com/job-agent/scrappers-mock.git@v0.1.0#subdirectory=packages/scrapper-service"
```

Monorepo for the Job Agent ecosystem: a LangGraph-powered backend that sanitizes CVs, evaluates job relevance, and stores results, plus a Telegram bot frontend for interacting with the pipeline. Supporting packages provide shared contracts and repository access.

## Packages

- `packages/job-agent-backend` — Orchestrator, LangGraph workflows, CV loader, filter service, and dependency container.
- `packages/telegram_bot` — Telegram client that guides users through uploading CVs, triggering searches, and reviewing relevant jobs.
- `packages/jobs-repository` — SQLAlchemy and Alembic powered persistence layer for storing job metadata.
- `packages/cvs-repository` — Lightweight filesystem repository for sanitized CV storage.
- `packages/job-agent-platform-contracts` — Shared Pydantic models and interfaces consumed across services.

## Prerequisites

- Python 3.9+
- PostgreSQL database (required for `jobs-repository` when persisting jobs)
- OpenAI API access (`OPENAI_API_KEY`), plus credentials for optional LangSmith tracing
- Telegram bot token from [@BotFather](https://t.me/botfather)
- Access to the shared scrapper service referenced by the backend configuration

## Repository Layout

```
job-agent-platform/
├── packages/
│   ├── job-agent-backend/
│   ├── telegram_bot/
│   ├── jobs-repository/
│   ├── cvs-repository/
│   └── contracts/
├── docker-compose.yml
├── docker-start.sh
├── pyproject.toml
└── README.md
```

## Development Workflow

- Run tests:

  ```bash
  cd packages/job-agent-backend && pytest
  cd packages/telegram_bot && pytest
  cd packages/jobs-repository && pytest
  ```

- Format and lint:

  ```bash
  black packages/*/src
  ruff check packages/*/src
  ```

### LangSmith Studio

1. Activate the repository virtual environment.
2. From the repository root run `langgraph dev`. The CLI reads `langgraph.json`, starts the local LangGraph API server, and opens the LangSmith Studio workspace mapped to your project.
3. If the browser does not open automatically, visit `https://smith.langchain.com/studio/dev/local` while the server is running.
4. Stop the server with `Ctrl+C` when you finish working in Studio.

## Architecture Highlights

1. **Job Agent Orchestrator** — Coordinates CV ingestion, job scraping, filtering, and workflow execution.
2. **LangGraph Workflows** — Modular pipelines for PII removal and job processing, backed by `langchain-openai` structured outputs.
3. **Repositories and Contracts** — Shared abstractions to persist sanitized CVs and relevant job metadata.
4. **Telegram Interface** — Async python-telegram-bot client delivering progress updates and final results to end users.

## Contributing

- Ensure tests and linters pass before submitting changes.
- Keep implementation code self-documenting (avoid inline comments) per repository guidelines.
- Open a pull request with a clear summary of changes and manual verification steps.

## License

Project licensing to be specified.
