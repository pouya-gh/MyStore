from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "TEST": {
            "NAME": "testdb.sqlite3",
        },
    }
}

INTERNAL_IPS = [
    '127.0.0.1',
    "localhost",
]