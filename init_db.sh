# init_db.sh

#!/bin/sh

# Wait for the database to be ready
while ! nc -z db 5432; do
  echo 'Waiting for DB...'
  sleep 0.1
done

# Run migrations
echo 'DB is ready! Running migrations...'
python manage.py migrate

# Create superuser if it doesn't exist
echo 'Creating superuser...'
python manage.py shell <<EOF
from django.contrib.auth.models import User
from django.core.management import call_command

try:
    user = User.objects.get(username='admin')
    print("Superuser already exists.")
except User.DoesNotExist:
    call_command('createsuperuser', username='admin', email='admin@example.com', password='changeme', interactive=False)
EOF

# Start the Django server
python manage.py runserver 0.0.0.0:8000
