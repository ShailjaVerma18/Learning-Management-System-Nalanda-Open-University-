#!/bin/bash
set -e

echo "========================================="
echo "Nalanda LMS - Docker Entrypoint"
echo "========================================="

# Validate required environment variables
echo "Checking environment variables..."
if [ -z "$DATABASE_NAME" ] || [ -z "$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ]; then
    echo "ERROR: Required environment variables are not set!"
    echo "Please ensure .env file exists and contains:"
    echo "  - DATABASE_NAME"
    echo "  - DATABASE_USER"
    echo "  - DATABASE_PASSWORD"
    exit 1
fi

echo "Environment variables validated successfully!"
echo "Database: $DATABASE_NAME"
echo "User: $DATABASE_USER"
echo "Host: ${POSTGRES_HOST:-db}"
echo ""

echo "Waiting for PostgreSQL to be ready..."
RETRY_COUNT=0
MAX_RETRIES=30
until nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERROR: PostgreSQL failed to start after $MAX_RETRIES attempts"
    exit 1
  fi
  echo "PostgreSQL is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done
echo "PostgreSQL is ready!"

# Wait for PostgreSQL to fully initialize
echo "Waiting for PostgreSQL to fully initialize..."
sleep 5

# Create database if it doesn't exist (connect to default postgres database)
echo "Checking/Creating database '$DATABASE_NAME'..."
DB_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h ${POSTGRES_HOST:-db} -U $POSTGRES_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DATABASE_NAME'")
if [ "$DB_EXISTS" != "1" ]; then
    echo "Database '$DATABASE_NAME' does not exist. Creating..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -h ${POSTGRES_HOST:-db} -U $POSTGRES_USER -d postgres -c "CREATE DATABASE $DATABASE_NAME"
    echo "Database '$DATABASE_NAME' created successfully!"
else
    echo "Database '$DATABASE_NAME' already exists."
fi

echo ""
echo "Running Django migrations..."
if python manage.py migrate --noinput; then
    echo "Migrations completed successfully!"
else
    echo "ERROR: Migrations failed!"
    exit 1
fi

echo ""
echo "Collecting static files..."
if python manage.py collectstatic --noinput --clear; then
    echo "Static files collected successfully!"
else
    echo "WARNING: Static files collection failed (non-critical)"
fi

# Create superuser if credentials are provided
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo ""
    echo "Creating superuser..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
        User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
        print('✓ Superuser created successfully')
        print('  Username: $DJANGO_SUPERUSER_USERNAME')
        print('  Password: $DJANGO_SUPERUSER_PASSWORD')
    else:
        print('✓ Superuser already exists')
except Exception as e:
    print(f'✗ Error creating superuser: {e}')
END
else
    echo ""
    echo "NOTE: Superuser credentials not provided. Skipping superuser creation."
fi

echo ""
echo "========================================="
echo "✓ Django application initialized!"
echo "========================================="
echo "Starting server..."
echo ""
exec "$@"
