#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# If arguments are passed, execute them (e.g., custom development command)
# Otherwise, start the production Gunicorn server
if [ $# -gt 0 ]; then
    echo "Executing custom command: $@"
    exec "$@"
else
    echo "Starting production Gunicorn server..."
    exec gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
fi
