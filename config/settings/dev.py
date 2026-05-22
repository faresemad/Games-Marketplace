from .base import *  # noqa: F401, F403
from .base import BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-x$u-fk$uj68c&d2nupak+irs&osm0rwm+-dnk5y5l=(9rq)8=k"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: list[str] = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
