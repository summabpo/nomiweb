#!/bin/sh

export DJANGO_SETTINGS_MODULE=nomiweb.settings.production

echo 'Applying migrations...'
python manage.py migrate --noinput

echo 'Running server...'
exec gunicorn --bind 0.0.0.0:8000 nomiweb.wsgi:application