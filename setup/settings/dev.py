import os
from django.core.management.utils import get_random_secret_key
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# In production, always set DJANGO_SECRET_KEY environment variable.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Database - use PostgreSQL if configured, otherwise SQLite
DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "sqlite3")

if DATABASE_ENGINE == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": os.environ.get("POSTGRES_HOST", "db"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": int(os.environ.get("POSTGRES_CONN_MAX_AGE", "60")),
            "OPTIONS": {
                "sslmode": os.environ.get("POSTGRES_SSLMODE", "prefer"),
            },
        }
    }
elif DATABASE_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("MYSQL_DB", "gabaritoac"),
            "USER": os.environ.get("MYSQL_USER", "gabaritoac"),
            "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
            "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
            "PORT": os.environ.get("MYSQL_PORT", "3306"),
            "CONN_MAX_AGE": int(os.environ.get("MYSQL_CONN_MAX_AGE", "60")),
            "OPTIONS": {
                "charset": "utf8mb4",
            },
        }
    }

try:
    from .local import *
except ImportError:
    pass
