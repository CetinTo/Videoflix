#!/bin/bash

echo "==================================="
echo "Videoflix Backend Starting..."
echo "==================================="

# Warte auf PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started!"

# Warte auf Redis
echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "Redis started!"

# Im videoflix-backend-Verzeichnis arbeiten (einziges Backend)
cd /app/videoflix-backend || exit 1

# Erstelle logs Verzeichnis
mkdir -p logs

# Erstelle Media Verzeichnisse
mkdir -p media/videos
mkdir -p media/thumbnails
mkdir -p media/profile_pictures

# Migrations ausführen
echo "Running migrations..."
python manage.py migrate --noinput

# Statische Dateien sammeln
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Superuser erstellen (falls nicht vorhanden)
echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
END

echo "==================================="
echo "Starting RQ Worker (default queue)..."
echo "==================================="
python manage.py rqworker default &
RQ_PID=$!
echo "RQ Worker started (PID $RQ_PID)"

echo "==================================="
echo "Starting Gunicorn..."
echo "==================================="

# Starte Gunicorn
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
