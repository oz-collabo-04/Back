#!/usr/bin/env bash
set -eo pipefail

# Docker 컨테이너 내부에서 pyenv 활성화 후, Django 테스트 실행
docker compose exec django_gunicorn bash -c "
  source ~/.bashrc && \
  pyenv activate django-collabo && \
  cd src && \
  poetry run python manage.py test reviews
"
