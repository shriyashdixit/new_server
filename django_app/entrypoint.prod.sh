#!/bin/sh

# Check if PostgreSQL is ready
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Start cron in the background
cron &

# Run Django management commands
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn django_project.wsgi:application --bind 0.0.0.0:8000

# Start supervisor to manage both the Django app and the Telegram bot
/usr/bin/supervisord
