# syntax=docker/dockerfile:1.6
# Enable BuildKit features like --mount=type=ssh

FROM python:3.11-slim as base

# Install git and ssh client for git+ssh dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client && \
    rm -rf /var/lib/apt/lists/*

# Pre-trust GitHub host key to avoid "Host key verification failed"
RUN mkdir -p -m 0700 /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

# Set working directory
WORKDIR /app

# ======================
# Install local packages
# ======================

# Copy and install jobs-repository (dependency of job-agent-backend)
COPY packages/jobs-repository /app/packages/jobs-repository
RUN pip install --no-cache-dir /app/packages/jobs-repository

RUN --mount=type=ssh ssh -T git@github.com || true

# Copy and install job-agent-backend
# (this one may pull git+ssh dependencies from private repos)
COPY packages/job-agent-backend /app/packages/job-agent-backend
RUN --mount=type=ssh pip install --no-cache-dir /app/packages/job-agent-backend

# Copy and install telegram_bot
COPY packages/telegram_bot /app/packages/telegram_bot
RUN pip install --no-cache-dir /app/packages/telegram_bot

# Set working directory to telegram_bot
WORKDIR /app/packages/telegram_bot

# Default command
CMD ["python", "-m", "telegram_bot.main"]