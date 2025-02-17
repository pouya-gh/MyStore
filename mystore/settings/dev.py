from .base import *
import dj_database_url

DEBUG = False

if not DEBUG:    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
