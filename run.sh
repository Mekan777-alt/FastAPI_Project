#!/bin/bash

# Wait for PostgreSQL to start
until psql -h "db" -U "$DB_USER" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Run the migrations
alembic upgrade head

# Start the application
uvicorn app:app --host 0.0.0.0 --port 8000