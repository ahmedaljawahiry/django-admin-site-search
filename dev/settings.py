"""Basic settings for local development and tests"""

from pathlib import Path

DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "NOT_A_SECRET"
ALLOWED_HOSTS = []
ROOT_URLCONF = "dev.urls"
STATIC_URL = "static/"
WSGI_APPLICATION = "dev.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dev.football.core",
    "dev.admin.CustomAdminConfig",
    "dev.football.players",
    "dev.football.stadiums",
    "dev.football.teams",
    "admin_site_search",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["dev/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# this drastically speeds up tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
