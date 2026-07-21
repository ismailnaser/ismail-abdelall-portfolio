#!/usr/bin/env bash
set -o errexit

# Collect CSS/JS into staticfiles/ so WhiteNoise can serve them
python manage.py collectstatic --no-input

# Create/update DB tables
python manage.py migrate --noinput
python manage.py ensure_superuser

# Bind to Render's $PORT
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
