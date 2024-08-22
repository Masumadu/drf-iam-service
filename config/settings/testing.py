from fakeredis import FakeConnection

from config.settings.base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SECRET_KEY = env("SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("TEST_DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://",
        "OPTIONS": {"connection_class": FakeConnection},
    }
}
