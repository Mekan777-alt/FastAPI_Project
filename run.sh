#!/bin/bash

source .env

sleep 3
Wait for PostgreSQL to start
until PGPASSWORD="${DBPASSWORD}" psql -h "db" -p "5432" -U "postgres" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Run the migrations
alembic upgrade head
echo "Alembic migrations done"

python3 db_data.py
echo "Data added to Database!!!"
#Start the application
uvicorn app:app --host 0.0.0.0 --port 8000