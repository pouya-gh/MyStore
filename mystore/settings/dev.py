from .base import *
import dj_database_url

DEBUG = False

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
