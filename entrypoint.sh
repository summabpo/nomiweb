#!/bin/sh

# Usar DJANGO_SETTINGS_MODULE del env si ya está definido (ej. dev), sino production
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  export DJANGO_SETTINGS_MODULE=nomiweb.settings.production
fi


# # Collect static files
echo "Collecting static files..."
#python manage.py collectstatic --noinput

# Run server with Gunicorn
echo 'Running server...'
exec gunicorn --bind 0.0.0.0:8000 nomiweb.wsgi:application --workers 3 --timeout 1200 --log-level debug
