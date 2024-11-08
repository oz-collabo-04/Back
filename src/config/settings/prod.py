from dotenv import dotenv_values

from config.settings.base import *

DEBUG = False

ENV = dotenv_values("../prod.env")
SECRET_KEY = ENV.get("DJANGO_SECRET_KEY", "dkanrjsk")

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": ENV.get("POSTGRES_HOST", "localhost"),
        "USER": ENV.get("POSTGRES_USER", "postgres"),
        "PASSWORD": ENV.get("POSTGRES_PASSWORD", "postgres"),
        "NAME": ENV.get("POSTGRES_DBNAME", "postgres"),
        "PORT": ENV.get("POSTGRES_PORT", 5432),
    }
}

# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
