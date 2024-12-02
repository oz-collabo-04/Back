import random

from dotenv import dotenv_values

from config.settings.base import *

DEBUG = False

ENV = dotenv_values("../prod.env")
SECRET_KEY = ENV.get(
    "DJANGO_SECRET_KEY", "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()?", k=50))
)

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": ENV.get("POSTGRES_HOST", "db"),
        "USER": ENV.get("POSTGRES_USER", "postgres"),
        "PASSWORD": ENV.get("POSTGRES_PASSWORD", "postgres"),
        "NAME": ENV.get("POSTGRES_DBNAME", "oz_collabo"),
        "PORT": ENV.get("POSTGRES_PORT", 5432),
    }
}

# OAuth
NAVER_CLIENT_ID = ENV.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = ENV.get("NAVER_CLIENT_SECRET", "")

KAKAO_CLIENT_ID = ENV.get("KAKAO_CLIENT_ID", "")

GOOGLE_CLIENT_ID = ENV.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = ENV.get("GOOGLE_CLIENT_SECRET", "")

# NCP Object Storage 설정
AWS_ACCESS_KEY_ID = (ENV.get("AWS_ACCESS_KEY_ID", ""),)
AWS_SECRET_ACCESS_KEY = (ENV.get("AWS_SECRET_ACCESS_KEY", ""),)
AWS_STORAGE_BUCKET_NAME = (ENV.get("AWS_STORAGE_BUCKET_NAME", ""),)
AWS_S3_ENDPOINT_URL = "https://kr.object.ncloudstorage.com"  # NCP Endpoint
AWS_S3_REGION_NAME = "kr-standard"  # 리전 (kr-standard)

# 정적 및 미디어 파일 설정
STATICFILES_STORAGE = "config.storages.StaticStorage"  # Static 파일 저장소
DEFAULT_FILE_STORAGE = "config.storages.s3boto3.MediaStorage"  # Media 파일 저장소

# 파일 URL 설정
AWS_QUERYSTRING_AUTH = False  # False로 설정하면 Public URL로 접근 가능

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_SECURE = True  # CSRF 쿠키를 HTTPS에서만 전송
