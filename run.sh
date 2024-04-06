#!/bin/bash

source .env

# Wait for PostgreSQL to start
until PGPASSWORD="${DBPASSWORD}" psql -h "172.29.0.2" -p "5432" -U "${DBUSER}" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Run the migrations
alembic upgrade head
# Start the application
uvicorn app:app --host 0.0.0.0 --port 8000