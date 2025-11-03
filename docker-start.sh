#!/bin/bash
set -e

echo "Starting Job Agent Platform..."

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your environment variables:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your actual values"
    exit 1
fi

# Start services
echo "Starting PostgreSQL and Telegram Bot..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-jobagent} -d ${POSTGRES_DB:-jobs} -c "SELECT 1;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "Database is ready!"
    echo ""
    echo "To run migrations, execute:"
    echo "  cd packages/jobs-repository"
    echo "  alembic upgrade head"
    echo ""
else
    echo "Warning: Database connection failed. Please check your configuration."
fi

echo "Services started successfully!"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f telegram_bot"
echo ""
echo "To stop services:"
echo "  docker-compose down"
