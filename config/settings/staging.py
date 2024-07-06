from config.settings.base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SECRET_KEY = env("SECRET_KEY")
