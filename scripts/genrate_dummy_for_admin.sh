#!/usr/bin/env bash

set -eo pipefail

docker-compose exec django_gunicorn bash -c "
source ~/.bashrc &&\
pyenv activate django-collabo &&\
cd src &&\
echo "Generate Dummy Data for admin..."
python manage.py generate_dummy_for_admin
"