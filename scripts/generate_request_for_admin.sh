#!/usr/bin/env bash

set -eo pipefail

docker-compose exec django_gunicorn bash -c "
source ~/.bashrc &&\
pyenv activate django-collabo &&\
cd src &&\
python manage.py generate_request_for_admin
"