#!/bin/bash

# 가상 환경 활성화
source ~/.bashrc
pyenv activate django-collabo

# 프로젝트 디렉토리로 이동
cd src

# 데이터베이스 마이그레이션
echo "Applying database migrations..."
python manage.py migrate --no-input

# 정적 파일 수집
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Gunicorn 실행
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
