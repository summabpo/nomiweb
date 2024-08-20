#!/bin/sh

# Export environment variables
export DJANGO_SETTINGS_MODULE=nomiweb.settings.production

# Apply migrations
# echo 'Applying migrations...'
# python manage.py migrate --noinput

# # Collect static files
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Run server with Gunicorn
echo 'Running server...'
exec gunicorn --bind 0.0.0.0:8000 nomiweb.wsgi:application --workers 3 --timeout 1200 --log-level debug
