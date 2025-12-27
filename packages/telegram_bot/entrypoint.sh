#!/bin/bash
set -e

echo "Running jobs-repository migrations..."
cd /app/packages/jobs-repository
alembic upgrade head

echo "Running essay-repository migrations..."
cd /app/packages/essay-repository
alembic upgrade head

echo "Starting Telegram bot..."
cd /app/packages/telegram_bot
exec python -u -m telegram_bot.main
