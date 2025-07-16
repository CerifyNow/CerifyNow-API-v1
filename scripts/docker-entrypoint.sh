#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_admin --email=admin@certifynow.uz --password=admin123

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Generate sample data in development
if [ "$DEBUG" = "True" ]; then
    echo "Generating sample data..."
    python manage.py generate_certificates --count=20
fi

echo "Starting application..."
exec "$@"
