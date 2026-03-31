import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure project root on sys.path so 'agents' package is importable
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SECRET_KEY = 'autogov-hackathon-secret-key-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Optional packages — don't crash if not installed
try:
    import corsheaders
    _HAS_CORS = True
except ImportError:
    _HAS_CORS = False

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
]
if _HAS_CORS:
    INSTALLED_APPS.insert(0, 'corsheaders')

MIDDLEWARE = []
if _HAS_CORS:
    MIDDLEWARE.append('corsheaders.middleware.CorsMiddleware')
MIDDLEWARE.append('django.middleware.common.CommonMiddleware')

ROOT_URLCONF = 'autogov.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
    ]},
}]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CORS_ALLOW_ALL_ORIGINS = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.json_exception_handler',
}
