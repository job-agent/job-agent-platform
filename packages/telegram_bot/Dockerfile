FROM python:3.11-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p -m 0700 /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

WORKDIR /app

COPY packages/job-agent-platform-contracts /app/packages/job-agent-platform-contracts
RUN pip install --no-cache-dir /app/packages/job-agent-platform-contracts

COPY packages/cvs-repository /app/packages/cvs-repository
RUN pip install --no-cache-dir /app/packages/cvs-repository

COPY packages/db-core /app/packages/db-core
RUN pip install --no-cache-dir /app/packages/db-core

COPY packages/jobs-repository /app/packages/jobs-repository
RUN pip install --no-cache-dir /app/packages/jobs-repository

COPY packages/essay-repository /app/packages/essay-repository
RUN pip install --no-cache-dir /app/packages/essay-repository

RUN --mount=type=ssh ssh -T git@github.com || true

COPY packages/job-agent-backend /app/packages/job-agent-backend
RUN --mount=type=ssh pip install --no-cache-dir /app/packages/job-agent-backend

RUN mkdir -p /usr/local/lib/python3.11/site-packages/data/cvs && \
    (cp -r /app/packages/job-agent-backend/src/data/* /usr/local/lib/python3.11/site-packages/data/ 2>/dev/null || true)

COPY packages/telegram_bot /app/packages/telegram_bot
RUN --mount=type=ssh pip install --no-cache-dir /app/packages/telegram_bot

COPY packages/telegram_bot/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /app/packages/telegram_bot

CMD ["/app/entrypoint.sh"]