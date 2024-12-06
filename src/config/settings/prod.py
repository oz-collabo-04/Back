import random

from dotenv import dotenv_values

from config.settings.base import *

DEBUG = True

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

# storages 설정
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "media",
            "default_acl": "public-read",
            "bucket_name": ENV.get("AWS_STORAGE_BUCKET_NAME", ""),  # S3 버킷 이름
            "access_key": ENV.get("AWS_ACCESS_KEY_ID", ""),  # AWS Access Key
            "secret_key": ENV.get("AWS_SECRET_ACCESS_KEY", ""),  # AWS Secret Key
            "region_name": ENV.get("AWS_S3_REGION_NAME", ""),  # AWS 리전
            "endpoint_url": ENV.get("AWS_S3_ENDPOINT_URL", "https://kr.object.ncloudstorage.com"),
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "public-read",
            "bucket_name": ENV.get("AWS_STORAGE_BUCKET_NAME", ""),  # S3 버킷 이름
            "access_key": ENV.get("AWS_ACCESS_KEY_ID", ""),  # AWS Access Key
            "secret_key": ENV.get("AWS_SECRET_ACCESS_KEY", ""),  # AWS Secret Key
            "region_name": ENV.get("AWS_S3_REGION_NAME", ""),  # AWS 리전
            "endpoint_url": ENV.get("AWS_S3_ENDPOINT_URL", "https://kr.object.ncloudstorage.com"),
        },
    },
}

# OAuth
NAVER_CLIENT_ID = ENV.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = ENV.get("NAVER_CLIENT_SECRET", "")

KAKAO_CLIENT_ID = ENV.get("KAKAO_CLIENT_ID", "")

GOOGLE_CLIENT_ID = ENV.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = ENV.get("GOOGLE_CLIENT_SECRET", "")

# 파일 URL 설정
AWS_QUERYSTRING_AUTH = False  # False로 설정하면 Public URL로 접근 가능

# 네이버 oauth
NAVER_CALLBACK_URL = ENV.get("NAVER_CALLBACK_URL", "")
NAVER_LOGIN_URL = ENV.get("NAVER_LOGIN_URL")
NAVER_TOKEN_URL = ENV.get("NAVER_TOKEN_URL")
NAVER_USER_INFO_URL = ENV.get("NAVER_USER_INFO_URL", "")

# 카카오 oauth
KAKAO_CALLBACK_URL = ENV.get("KAKAO_CALLBACK_URL", "")
KAKAO_LOGIN_URL = ENV.get("KAKAO_LOGIN_URL", "")
KAKAO_TOKEN_URL = ENV.get("KAKAO_TOKEN_URL", "")
KAKAO_USER_INFO_URL = ENV.get("KAKAO_USER_INFO_URL", "")
KAKAO_ACCESS_TOKEN_INFO_URL = ENV.get("KAKAO_ACCESS_TOKEN_INFO_URL", "")

# 구글 oauth
GOOGLE_REDIRECT_URI = ENV.get("GOOGLE_REDIRECT_URI", "")
GOOGLE_TOKEN_URL = ENV.get("GOOGLE_TOKEN_URL", "")
GOOGLE_USER_INFO_URL = ENV.get("GOOGLE_USER_INFO_URL")
