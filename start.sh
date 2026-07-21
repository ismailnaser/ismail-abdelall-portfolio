#!/usr/bin/env bash
set -o errexit

# Create/update DB tables on every start (fixes missing tables on Render Postgres)
python manage.py migrate --noinput
python manage.py ensure_superuser

# Bind to Render's $PORT
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
