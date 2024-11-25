from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "default-oz-collabo-servi-18d66-100596032-ce8f2faf2e3d.kr.lb.naverncp.com",
]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

CUSTOM_APPS = [
    "common",
    "users",
    "expert",
    "chat",
    "estimations",
    "notifications",
    "reservations",
    "reviews",
]

THIRDPARTY_APPS = [
    "rest_framework",
    "drf_spectacular",
    "django_redis",
    "channels_redis",
    "storages",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_extensions",
    "multiselectfield",
]

INSTALLED_APPS = DJANGO_APPS + CUSTOM_APPS + THIRDPARTY_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "users.User"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "UPDATE_LAST_LOGIN": True,
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "so_new_api",
    "DESCRIPTION": "so_new_wedding",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# 네이버 oauth
NAVER_CALLBACK_URL = "http://localhost:5173/login/naver/callback/"
NAVER_LOGIN_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"

# 카카오 oauth
KAKAO_CALLBACK_URL = (
    "http://localhost:5173/login/kakao/callback/"  # 카카오 콜백 URL, 카카오 인증후 리디렉션될 URL
)
KAKAO_LOGIN_URL = (
    "https://kauth.kakao.com/oauth/authorize"  # 카카오 로그인 URL, 카카오 로그인 요청 URL,인증페이지로 이동
)
KAKAO_TOKEN_URL = (
    "https://kauth.kakao.com/oauth/token"  # 카카오 액세스 토큰 URL, 인증코드로 액세스토큰을 교환하는 URL,리프레쉬?
)
KAKAO_USER_INFO_URL = (
    "https://kapi.kakao.com/v2/user/me"  # 카카오 사용자 정보 URL, 카카오 사용자 정보를 가져오기 위한 URL
)
KAKAO_ACCESS_TOKEN_INFO_URL = "https://kapi.kakao.com/v1/user/access_token_info"  # 액세스 토큰 정보 확인 URL, 발급된 액세스 토큰의 유효성을 확인하기 위한 URL

# 구글 oauth
GOOGLE_REDIRECT_URI = "http://localhost:5173/login/google/callback/"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"