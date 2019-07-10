#!/usr/bin/env sh

# Run migrations
python manage.py migrate

# Create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | python manage.py shell

# Run the server
python manage.py runserver --settings gradify.settings.heroku 0.0.0.0:$PORT

