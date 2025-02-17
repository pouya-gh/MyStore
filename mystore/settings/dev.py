from .base import *
import dj_database_url

DEBUG = False

if envrion_vars("ALLOWED_HOSTS"):
    ALLOWED_HOSTS = envrion_vars("ALLOWED_HOSTS").split("|")
else:
    ALLOWED_HOSTS = []

DATABASES = {
    "default": dj_database_url.config(
        default=envrion_vars("POSTGRESQL_URL"),
        conn_max_age=600
    )
}

INTERNAL_IPS = [
    '127.0.0.1',
    "localhost",
]
