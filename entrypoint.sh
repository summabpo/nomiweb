#!/bin/sh

export DJANGO_SETTINGS_MODULE=nomiweb.settings.production

#echo 'Applying migrations...'
#python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
#python manage.py collectstatic --noinput

echo 'Running server...'
exec gunicorn --bind 0.0.0.0:8000 nomiweb.wsgi:application --workers 3