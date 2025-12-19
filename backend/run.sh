#!/bin/sh

set -e

echo "Waiting for PostgreSQL to start..."
python << END
import sys
import time
import socket
import os

host = os.getenv("POSTGRES_SERVER", "db")
port = int(os.getenv("POSTGRES_PORT", 5432))

start_time = time.time()
while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        if time.time() - start_time > 30:
            print("Timeout waiting for Database.")
            sys.exit(1)
        time.sleep(1)
        print("Waiting for DB...")
END

echo "Database is up!"

echo "Running Alembic Migrations..."
alembic upgrade head

echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload