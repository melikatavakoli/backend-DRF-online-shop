#!/bin/sh
set -e

echo "Waiting 10 seconds for database to be ready..."
sleep 10

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8001
