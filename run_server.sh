#!/usr/bin/env sh

# Run migrations
python manage.py migrate

# Create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | python manage.py shell

# Configure allauth
GC_CLIENT_ID='test_id'
GC_SECRET='test_secret'
echo "from django.contrib.sites.models import Site; from allauth.socialaccount.models import SocialApp; heroku_site = Site.objects.create(domain='herokuapp.com', name='heroku'); allauth_app = SocialApp.objects.create(client_id='$GC_CLIENT_ID', provider='google', name='google_classroom', secret='$GC_SECRET'); allauth_app.sites.add(heroku_site); allauth_app.save" | python manage.py shell

# Run the server
python manage.py runserver --settings gradify.settings.heroku 0.0.0.0:$PORT

