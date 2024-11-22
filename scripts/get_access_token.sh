#!/usr/bin/env bash

set -eo pipefail

docker-compose exec django_gunicorn bash -c "
source ~/.bashrc &&\
pyenv activate django-collabo &&\
cd src &&\
python manage.py shell_plus << END

from rest_framework_simplejwt.tokens import RefreshToken
user = User.objects.get(email='admin@example.com')
refresh = RefreshToken.for_user(user)
access = str(refresh.access_token)

print('Testing Access Token: ', access)

END"