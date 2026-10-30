#!/bin/sh
set -e

echo "=== Sudur Chinari Backend Entrypoint ==="

# Wait for PostgreSQL if configured
if [ "$DB_ENGINE" = "postgres" ] || [ "$DB_ENGINE" = "postgresql" ]; then
    DB_HOST="${POSTGRES_HOST:-${DB_HOST:-db}}"
    DB_PORT="${POSTGRES_PORT:-${DB_PORT:-5432}}"
    echo "Waiting for PostgreSQL database at ${DB_HOST}:${DB_PORT}..."
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 1
    done
    echo "Database is ready!"
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Auto-create superuser if credentials are provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Ensuring superuser exists..."
    python manage.py createsuperuser --noinput || true
fi

# Auto-seed database if requested
if [ "$AUTO_SEED" = "true" ] || [ "$AUTO_SEED" = "1" ]; then
    echo "Seeding initial mock data..."
    python manage.py seed_mock_data || true
    python manage.py seed_menu_categories || true
    python manage.py seed_district_partners || true
    python manage.py update_translation_fields || true
fi

echo "Starting server: $@"
exec "$@"
