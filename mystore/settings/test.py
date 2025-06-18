# TODO: remove this file. this should be needed anymore.

from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

INTERNAL_IPS = [
    '127.0.0.1',
    "localhost",
]
