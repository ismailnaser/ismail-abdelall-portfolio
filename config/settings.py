from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-change-me-before-production",
)

DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")


def _parse_hosts(raw: str) -> list[str]:
    hosts = []
    for part in raw.split(","):
        host = part.strip()
        if not host:
            continue
        # Allow pasting full URLs by mistake
        host = host.replace("https://", "").replace("http://", "")
        host = host.split("/")[0].strip()
        if host:
            hosts.append(host)
    return hosts


ALLOWED_HOSTS = _parse_hosts(
    os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com")
)
# Always allow Render subdomains as a safety net
if ".onrender.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".onrender.com")

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main.apps.MainConfig",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
                "main.context_processors.site_profile",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database: use DATABASE_URL on Render (Postgres), else local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    import dj_database_url

    # Render sometimes gives postgres:// — normalize for psycopg3
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=not DATABASE_URL.startswith("postgresql://") or "127.0.0.1" not in DATABASE_URL and "localhost" not in DATABASE_URL,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

LANGUAGE_CODE = "ar"
TIME_ZONE = "Asia/Gaza"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)


def _clean_env(name: str) -> str:
    value = (os.environ.get(name) or "").strip().strip('"').strip("'")
    bad_markers = ("your_api_key", "your_api_secret", "your_cloud_name", "<", "changeme", "xxx")
    low = value.lower()
    if not value or any(m in low for m in bad_markers):
        return ""
    return value


# Use Cloudinary for uploaded images when REAL credentials exist (Render).
_cloudinary_url = _clean_env("CLOUDINARY_URL")
_cloud_name = _clean_env("CLOUDINARY_CLOUD_NAME")
_api_key = _clean_env("CLOUDINARY_API_KEY")
_api_secret = _clean_env("CLOUDINARY_API_SECRET")

# If URL still contains placeholders, ignore it
if _cloudinary_url and (
    "your_api_key" in _cloudinary_url.lower()
    or "<" in _cloudinary_url
    or ":@" in _cloudinary_url
):
    _cloudinary_url = ""

USE_CLOUDINARY = bool(_cloudinary_url or (_cloud_name and _api_key and _api_secret))

if USE_CLOUDINARY:
    import cloudinary

    INSTALLED_APPS = list(INSTALLED_APPS) + ["cloudinary", "cloudinary_storage"]

    if _cloudinary_url:
        os.environ["CLOUDINARY_URL"] = _cloudinary_url
        cloudinary.config(secure=True)
    else:
        # Clear a bad CLOUDINARY_URL so the package doesn't prefer it
        os.environ.pop("CLOUDINARY_URL", None)
        os.environ["CLOUDINARY_CLOUD_NAME"] = _cloud_name
        os.environ["CLOUDINARY_API_KEY"] = _api_key
        os.environ["CLOUDINARY_API_SECRET"] = _api_secret
        cloudinary.config(
            cloud_name=_cloud_name,
            api_key=_api_key,
            api_secret=_api_secret,
            secure=True,
        )
        # django-cloudinary-storage reads this dict
        CLOUDINARY_STORAGE = {
            "CLOUD_NAME": _cloud_name,
            "API_KEY": _api_key,
            "API_SECRET": _api_secret,
            "SECURE": True,
        }

    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    # Avoid package picking up placeholder CLOUDINARY_URL from the environment
    for key in (
        "CLOUDINARY_URL",
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
    ):
        val = (os.environ.get(key) or "").lower()
        if "your_api" in val or "<" in val:
            os.environ.pop(key, None)

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Show full errors in Render Logs when DEBUG=False
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

