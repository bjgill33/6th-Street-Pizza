from pathlib import Path
from dotenv import load_dotenv, dotenv_values
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load Environmental Variables
load_dotenv()

env = {
    **dotenv_values(BASE_DIR / ".env.dev"),  # load shared development variables
    **dotenv_values(BASE_DIR / ".env.prod"),  # load sensitive variables
}

SECRET_KEY = env["DJANGO_SECRET_KEY"]

STRIPE_SECRET_KEY = env["STRIPE_SECRET_KEY"]
STRIPE_PUBLIC_KEY = env["STRIPE_PUBLIC_KEY"]

DEBUG = True

ALLOWED_HOSTS = [
    "6thstreetpizza.store",
    "www.6thstreetpizza.store",
    "5.181.218.74",
    "localhost",
    "files.6thstreetpizza.store",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "myproject.wsgi.application"


# Database

DATABASE_TYPE = env["DATABASE_TYPE"]

DATABASES = {}

if DATABASE_TYPE == "SQLITE":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif DATABASE_TYPE == "MYSQL":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env["MYSQL_DB_NAME"],
            "USER": env["MYSQL_DB_USER"],
            "PASSWORD": env["MYSQL_DB_PASSWORD"],
            "HOST": env["MYSQL_DB_HOST"],
            "PORT": env["MYSQL_DB_PORT"],
            "OPTIONS": {
                "charset": "utf8mb4",  # Ensure full Unicode support
            },
        }
    }
else:
    raise Exception(
        f'Unknown configuration value in .env: DATABASE_TYPE. DATABASE_TYPE="{DATABASE_TYPE}"\n\t Valid values include: SQLITE, MYSQL'
    )

# Password validation


AUTH_USER_MODEL = "accounts.CustomUser"

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

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Local database override
