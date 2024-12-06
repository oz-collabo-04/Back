import random

from dotenv import dotenv_values

from config.settings.base import *

DEBUG = True

ENV = dotenv_values("../local.env")
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

# Static
STATIC_URL = "static/"
STATIC_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / ".static_root"

# Media
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# OAuth
NAVER_CLIENT_ID = ENV.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = ENV.get("NAVER_CLIENT_SECRET", "")

KAKAO_CLIENT_ID = ENV.get("KAKAO_CLIENT_ID", "")

GOOGLE_CLIENT_ID = ENV.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = ENV.get("GOOGLE_CLIENT_SECRET", "")

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
