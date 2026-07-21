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
    "jazzmin",
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
            ssl_require=True,
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

# WhiteNoise serves collected static files in production
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Plain storage is more reliable on Render than compressed/manifest
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

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

JAZZMIN_SETTINGS = {
    "site_title": "لوحة التحكم",
    "site_header": "إدارة المعرض",
    "site_brand": "Portfolio",
    "site_logo_classes": "img-circle",
    "welcome_sign": "أهلاً بك — عدّل محتوى موقعك من هنا بسهولة",
    "copyright": "Portfolio Admin",
    "search_model": ["main.Project", "main.ContactMessage", "main.Skill"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "عرض الموقع", "url": "/", "new_window": True},
        {
            "name": "إعدادات الموقع",
            "url": "/admin/main/sitesettings/1/change/",
            "permissions": ["main.change_sitesettings"],
        },
        {"name": "المشاريع", "url": "/admin/main/project/", "permissions": ["main.view_project"]},
        {
            "name": "الرسائل",
            "url": "/admin/main/contactmessage/",
            "permissions": ["main.view_contactmessage"],
        },
    ],
    "show_sidebar": False,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "main",
        "main.SiteSettings",
        "main.Project",
        "main.Service",
        "main.Skill",
        "main.AboutPoint",
        "main.NavItem",
        "main.ContactMessage",
        "auth",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "main.SiteSettings": "fas fa-sliders-h",
        "main.Project": "fas fa-briefcase",
        "main.ProjectImage": "fas fa-images",
        "main.Service": "fas fa-hands-helping",
        "main.Skill": "fas fa-code",
        "main.AboutPoint": "fas fa-user-check",
        "main.NavItem": "fas fa-bars",
        "main.ContactMessage": "fas fa-envelope",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": "css/admin-custom.css",
    "custom_js": "js/admin-image-preview.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "main.sitesettings": "horizontal_tabs",
        "main.project": "horizontal_tabs",
        "main.contactmessage": "single",
        "main.skill": "single",
        "main.navitem": "single",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-success",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "flatly",
    "default_theme_mode": "light",
    "button_classes": {
        "primary": "btn-success",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}
