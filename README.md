# Job Agent Platform

A LangGraph-powered job search assistant with microservice architecture. The platform uses RabbitMQ for asynchronous job scraping, processes CVs to remove PII, evaluates job relevance using AI, and delivers results through a Telegram bot interface.

## Architecture Overview

The platform consists of three main components:

1. **Job Agent Platform** (this repository) - Main orchestrator with Telegram bot, LangGraph workflows, and repositories
2. **Scrapper Service** - Microservice that scrapes job listings from external sources and communicates via RabbitMQ
3. **Infrastructure** - PostgreSQL for data persistence and RabbitMQ for message queuing

```
┌─────────────────────┐         ┌──────────────────┐
│  Telegram Bot       │         │  RabbitMQ        │
│  (User Interface)   │         │  Message Broker  │
└──────────┬──────────┘         └────────┬─────────┘
           │                              │
           │                              │
           v                              v
┌─────────────────────────────────────────────────┐
│         Job Agent Backend                       │
│  - LangGraph Workflows (CV sanitization,        │
│    job filtering)                                │
│  - RabbitMQ Publisher/Consumer                  │
│  - Job & CV Repositories                        │
└──────────┬──────────────────────────────────────┘
           │
           v
┌─────────────────────┐
│  PostgreSQL         │
│  (Data Persistence) │
└─────────────────────┘

External Microservice (choose one):
┌─────────────────────────────────────────────────┐
│  Scrapper Service (Real or Mock)                │
│  - Consumes scrape requests from RabbitMQ       │
│  - Scrapes jobs from external sources           │
│  - Publishes results back via RabbitMQ          │
└─────────────────────────────────────────────────┘
```

## Quick Start

Get the platform running in 5 minutes:

```bash
# 1. Clone and configure
git clone <this-repo>
cd job-agent-platform
cp .env.example .env  # Edit with your API keys

# 2. Start infrastructure
docker compose up -d postgres rabbitmq

# 3. Start mock scrapper service
cd ../scrappers-mock
docker compose up -d

# 4. Apply database migrations
cd ../job-agent-platform
cd packages/jobs-repository
alembic upgrade head
cd ../..

# 5. Start the Telegram bot
docker compose up -d telegram_bot

# 6. Check logs
docker compose logs telegram_bot -f
```

Your bot should now be running and ready to receive messages on Telegram!

## Detailed Setup Instructions

### 1. Configure Environment Variables

Copy or rename `.env.example` to `.env` and populate it with the required variables (see [Required Environment Variables](#required-environment-variables) section below).

### 2. Start Infrastructure Services

Start PostgreSQL and RabbitMQ using Docker Compose:

```bash
docker compose up -d postgres rabbitmq
```

This will start:
- PostgreSQL on port 5432
- RabbitMQ on port 5672 (AMQP) and 15672 (Management UI)

### 3. Choose and Start a Scrapper Service

You have two options:

#### Option A: Use Mock Scrapper Service (Recommended for Development)

The mock service returns pre-defined job listings without actually scraping external sources:

```bash
# Clone the mock service repository (if not already cloned)
git clone <scrappers-mock-repo-url>

# Start the mock service
cd scrappers-mock
docker compose up -d
```

The mock service will:
- Connect to RabbitMQ automatically
- Return 10 pre-defined job listings
- Work without requiring external API credentials

#### Option B: Implement Your Own Scrapper Service

To use real job scraping, you need to implement a scrapper service that:

1. Consumes messages from the `job.scrape.request` RabbitMQ queue
2. Implements the scraping logic for your target job boards
3. Publishes results back to the reply queue specified in the request

The service must follow the contract defined in [job-scrapper-contracts](https://github.com/job-agent/job-scrapper-contracts):

**Request Format:**
```python
{
    "salary": 4000,           # Minimum salary
    "employment": "remote",   # Employment type
    "posted_after": "2025-10-01T00:00:00",  # ISO datetime
    "timeout": 30            # Request timeout in seconds
}
```

**Response Format:**
```python
{
    "jobs": [...],           # List of job dictionaries
    "success": true,         # Whether the scraping succeeded
    "error": null,           # Error message if failed
    "jobs_count": 10         # Number of jobs returned
}
```

Reference implementation: [scrappers repository](https://github.com/job-agent/scrappers)

### 4. Apply Database Migrations

```bash
# Jobs repository
cd packages/jobs-repository
alembic upgrade head

# Essay repository (includes pgvector extension setup)
cd ../essay-repository
alembic upgrade head
```

### 5. Start the Telegram Bot

Using Docker Compose (recommended):

```bash
docker compose up -d telegram_bot
```

Or run directly with Python:

```bash
python -m telegram_bot.main
```

## Required Environment Variables

Create a `.env` file in the repository root with the following variables:

### Core Services

- `OPENAI_API_KEY` — Required. API key for OpenAI models used in LangGraph workflows for CV sanitization and job filtering.
- `TELEGRAM_BOT_TOKEN` — Required. Token issued by @BotFather to connect your bot to Telegram.

### Database (PostgreSQL)

- `DATABASE_URL` — Required. Full PostgreSQL connection string, e.g., `postgresql://user:password@localhost:5432/dbname`
- `POSTGRES_USER` — Required. PostgreSQL username for database connections.
- `POSTGRES_PASSWORD` — Required. PostgreSQL password for the specified user.
- `POSTGRES_DB` — Required. Name of the PostgreSQL database.
- `POSTGRES_PORT` — Required. Port where PostgreSQL is running (default: 5432).

### Message Broker (RabbitMQ)

- `RABBITMQ_URL` — Required. AMQP connection URL, e.g., `amqp://jobagent:jobagent@localhost:5672/`
- `RABBITMQ_USER` — Required. RabbitMQ username (default: jobagent).
- `RABBITMQ_PASSWORD` — Required. RabbitMQ password (default: jobagent).
- `RABBITMQ_VHOST` — Required. RabbitMQ virtual host (default: /).
- `RABBITMQ_PORT` — Required. RabbitMQ AMQP port (default: 5672).
- `RABBITMQ_MANAGEMENT_PORT` — Optional. RabbitMQ Management UI port (default: 15672).

### Optional - Access Control

- `TELEGRAM_ALLOWED_USER_IDS` — Optional. Comma-separated list of Telegram user IDs allowed to use the bot. If not set or empty, all users can access the bot. To find your Telegram user ID, message [@userinfobot](https://t.me/userinfobot). Example: `123456789,987654321`

### Optional - LangSmith Tracing

- `LANGSMITH_API_KEY` — Optional. Enables LangSmith tracing and analytics for LangGraph workflow runs.
- `LANGSMITH_TRACING_V2` — Optional. Set to `true` to enable LangSmith v2 tracing.
- `LANGSMITH_PROJECT` — Optional. LangSmith project name for organizing traces.

### Example .env File

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABC...
# Restrict bot access (optional, omit to allow all users)
TELEGRAM_ALLOWED_USER_IDS=123456789

# PostgreSQL
DATABASE_URL=postgresql://jobagent:password123@localhost:5432/job_agent
POSTGRES_USER=jobagent
POSTGRES_PASSWORD=password123
POSTGRES_DB=job_agent
POSTGRES_PORT=5432

# RabbitMQ
RABBITMQ_URL=amqp://jobagent:jobagent@localhost:5672/
RABBITMQ_USER=jobagent
RABBITMQ_PASSWORD=jobagent
RABBITMQ_VHOST=/
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672

# LangSmith (optional)
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT=job-agent
LANGSMITH_API_KEY=ls__...
```

## Packages

- `packages/job-agent-backend` — Core orchestrator with LangGraph workflows, RabbitMQ integration, CV loader, filter service, and dependency container.
- `packages/telegram_bot` — Async Telegram client that guides users through uploading CVs, triggering searches, and reviewing relevant jobs.
- `packages/db-core` — Shared database infrastructure providing `BaseRepository`, session management, and transaction handling.
- `packages/jobs-repository` — Job persistence layer built on db-core with Alembic migrations.
- `packages/essay-repository` — Essay Q&A persistence layer built on db-core with Alembic migrations. Includes hybrid search (pgvector + full-text) via `EssaySearchService`.
- `packages/cvs-repository` — Lightweight filesystem repository for sanitized CV storage.
- `packages/job-agent-platform-contracts` — Shared Pydantic models and interfaces consumed across services.

## Prerequisites

- **Python 3.9+** for running the platform services
- **Docker & Docker Compose** for running infrastructure (PostgreSQL, RabbitMQ) and optional containerized deployment
- **PostgreSQL database with pgvector** for persisting job metadata, essay data, and vector embeddings
- **RabbitMQ** for asynchronous message queuing between services
- **OpenAI API key** for LangGraph workflows (CV sanitization, job filtering) and text embeddings
- **Telegram bot token** from [@BotFather](https://t.me/botfather)
- **Scrapper service** (either mock or custom implementation) running and connected to RabbitMQ

## Repository Layout

```
job-agent-platform/
├── packages/
│   ├── job-agent-backend/
│   ├── telegram_bot/
│   ├── db-core/                  # Shared database infrastructure
│   ├── jobs-repository/          # Depends on db-core
│   ├── essay-repository/         # Depends on db-core
│   ├── cvs-repository/
│   └── job-agent-platform-contracts/
├── docker-compose.yml
├── docker-start.sh
├── pyproject.toml
└── README.md
```

## Development Workflow

### Running Tests

```bash
cd packages/job-agent-backend && pytest
cd packages/telegram_bot && pytest
cd packages/jobs-repository && pytest
cd packages/essay-repository && pytest
```

### Code Formatting and Linting

```bash
black packages/*/src
ruff check packages/*/src
```

### Managing Services

**Start all infrastructure services:**
```bash
docker compose up -d postgres rabbitmq
```

**View logs:**
```bash
# Platform services
docker compose logs telegram_bot -f

# RabbitMQ
docker compose logs rabbitmq -f

# Mock scrapper service (from scrappers-mock directory)
cd scrappers-mock && docker compose logs scrapper_service_mock -f
```

**Stop services:**
```bash
# Stop platform services
docker compose down

# Stop mock scrapper (from scrappers-mock directory)
cd scrappers-mock && docker compose down
```

**Access RabbitMQ Management UI:**
Open http://localhost:15672 in your browser (default credentials: jobagent/jobagent)

### Switching Between Real and Mock Scrapper Services

To switch from real to mock:
```bash
# Stop real scrapper
cd scrappers && docker compose down

# Start mock scrapper
cd scrappers-mock && docker compose up -d
```

To switch from mock to real:
```bash
# Stop mock scrapper
cd scrappers-mock && docker compose down

# Start real scrapper
cd scrappers && docker compose up -d
```

### LangSmith Studio

1. Activate the repository virtual environment.
2. From the repository root run `langgraph dev`. The CLI reads `langgraph.json`, starts the local LangGraph API server, and opens the LangSmith Studio workspace mapped to your project.
3. If the browser does not open automatically, visit `https://smith.langchain.com/studio/dev/local` while the server is running.
4. Stop the server with `Ctrl+C` when you finish working in Studio.

## Architecture Highlights

1. **Microservice Architecture** — Decoupled services communicating via RabbitMQ message broker, enabling independent scaling and deployment.
2. **Job Agent Orchestrator** — Coordinates CV ingestion, job scraping (via RabbitMQ), filtering, and workflow execution.
3. **LangGraph Workflows** — Modular AI pipelines for PII removal and job relevance evaluation, backed by `langchain-openai` structured outputs.
4. **Asynchronous Job Scraping** — RabbitMQ-based request/response pattern enables non-blocking job scraping with timeout handling and error recovery.
5. **Repositories and Contracts** — Shared abstractions to persist sanitized CVs and relevant job metadata across services.
6. **Telegram Interface** — Async python-telegram-bot client delivering real-time progress updates and final results to end users.

## Troubleshooting

### Scrapper Service Authentication Errors

If you see `ACCESS_REFUSED - Login was refused using authentication mechanism PLAIN`:

1. Check that `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, and `RABBITMQ_VHOST` are set in your `.env` file
2. Verify the scrapper service is using the same credentials
3. Restart the scrapper service after updating credentials

### RabbitMQ Connection Issues

If services can't connect to RabbitMQ:

1. Verify RabbitMQ is running: `docker compose ps rabbitmq`
2. Check RabbitMQ logs: `docker compose logs rabbitmq`
3. Verify the network: `docker network ls | grep job-agent-network`
4. Ensure all services are on the same network in docker-compose.yml

### Database Migration Errors

If Alembic migrations fail:

1. Ensure PostgreSQL is running and accessible
2. Verify `DATABASE_URL` in `.env` is correct
3. Check database credentials and permissions
4. Try running migrations with verbose output: `alembic upgrade head --verbose`

### Telegram Bot Not Responding

If the bot doesn't respond to messages:

1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Check bot logs: `docker compose logs telegram_bot -f`
3. Ensure the bot is started: `docker compose ps telegram_bot`
4. Verify RabbitMQ connection is established
5. If `TELEGRAM_ALLOWED_USER_IDS` is set, verify your Telegram user ID is in the list (unauthorized users are silently ignored)

## Contributing

- Ensure tests and linters pass before submitting changes.
- Keep implementation code self-documenting (avoid inline comments) per repository guidelines.
- Open a pull request with a clear summary of changes and manual verification steps.

## Additional Resources

- [Job Scrapper Contracts Repository](https://github.com/job-agent/job-scrapper-contracts) - Shared contracts between platform and scrapper services
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html) - Official RabbitMQ documentation
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - LangGraph framework documentation
- [Python Telegram Bot](https://python-telegram-bot.org/) - python-telegram-bot library documentation

## License

Project licensing to be specified.
