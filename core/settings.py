from pathlib import Path
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".vercel.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "cloudinary_storage",
    "cloudinary",

    "pages",
    "products",
    "cart",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

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

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
}

MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#INFINITEPAY
INFINITEPAY_HANDLE = config("INFINITEPAY_HANDLE", default="")
SITE_URL = config("SITE_URL", default="https://riskclube.vercel.app")

#MELHORENVIO
MELHOR_ENVIO_TOKEN = config("MELHOR_ENVIO_TOKEN", default="")
MELHOR_ENVIO_ORIGIN_CEP = config("MELHOR_ENVIO_ORIGIN_CEP", default="")
MELHOR_ENVIO_ENV = config("MELHOR_ENVIO_ENV", default="sandbox")
FREE_SHIPPING_LIMIT = config("FREE_SHIPPING_LIMIT", default=250, cast=int)