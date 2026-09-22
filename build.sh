#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (WhiteNoise serves them)
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# One-time superuser bootstrap
# Safe: no-ops if the user already exists or DJANGO_SUPERUSER_PASSWORD is not set
python create_superuser.py