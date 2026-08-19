"""
GARL - Global Academic Research Library
Django Settings
"""

import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

# ──────────────────────────────────────────────────────────────────────────────
# Base directory
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# Security
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='.onrender.com,.vercel.app,localhost,127.0.0.1',
    cast=Csv(),
)
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    ALLOWED_HOSTS.append(os.environ['RENDER_EXTERNAL_HOSTNAME'])
# ──────────────────────────────────────────────────────────────────────────────
# Application definition
# ──────────────────────────────────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
]

LOCAL_APPS = [
    'accounts',
    'core',
    'dashboard',
    'research',
    'publishing',
    'innovation',
    'learning',
    'health_science',
    'library',
    'events',
    'community',
    'support',
    'notifications',
    'search',
    'analytics',
    'ai_support',
    'payments',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ──────────────────────────────────────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ──────────────────────────────────────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'core.context_processors.garl_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ──────────────────────────────────────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ──────────────────────────────────────────────────────────────────────────────
# Custom user model
# ──────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

# ──────────────────────────────────────────────────────────────────────────────
# Password validation
# ──────────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('es', 'Español'),
    ('ar', 'العربية'),
    ('zh-hans', '中文'),
    ('pt', 'Português'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# ──────────────────────────────────────────────────────────────────────────────
# Static files
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ──────────────────────────────────────────────────────────────────────────────
# Media files
# ──────────────────────────────────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────────────────────────────────────────
# Default primary key
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────────────────────────────────────
# Authentication
# ──────────────────────────────────────────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ──────────────────────────────────────────────────────────────────────────────
# Email
# ──────────────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = 'GARL <noreply@garl.edu>'

# ──────────────────────────────────────────────────────────────────────────────
# Crispy forms
# ──────────────────────────────────────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ──────────────────────────────────────────────────────────────────────────────
# File uploads
# ──────────────────────────────────────────────────────────────────────────────
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 MB

ALLOWED_DOCUMENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

# ──────────────────────────────────────────────────────────────────────────────
# Security headers (production only)
# ──────────────────────────────────────────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ──────────────────────────────────────────────────────────────────────────────
# CSRF — fix 403 on POST forms
# ──────────────────────────────────────────────────────────────────────────────
CSRF_COOKIE_HTTPONLY = False      # JS needs to read the token
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
for origin in config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv()):
    if origin and origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)
if os.environ.get('RENDER_EXTERNAL_URL'):
    CSRF_TRUSTED_ORIGINS.append(os.environ['RENDER_EXTERNAL_URL'])

# ──────────────────────────────────────────────────────────────────────────────
# Session
# ──────────────────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE = 86400 * 7   # 7 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ──────────────────────────────────────────────────────────────────────────────
# Pagination
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_PAGE_SIZE = 20
SEARCH_PAGE_SIZE = 15

# ──────────────────────────────────────────────────────────────────────────────
# GARL platform settings
# ──────────────────────────────────────────────────────────────────────────────
GARL_SITE_NAME = config('SITE_NAME', default='Global Academic Research Library')
GARL_SITE_URL  = config('SITE_URL',  default='http://localhost:8000')
GARL_VERSION   = '1.0.0'

# ──────────────────────────────────────────────────────────────────────────────
# AI Support Assistant
# ──────────────────────────────────────────────────────────────────────────────
GARL_AI_API_KEY  = config('GARL_AI_API_KEY',  default='')
GARL_AI_API_URL  = config('GARL_AI_API_URL',  default='https://api.openai.com/v1/chat/completions')
GARL_AI_MODEL    = config('GARL_AI_MODEL',    default='gpt-3.5-turbo')
GARL_AI_MAX_HISTORY = 100

# ──────────────────────────────────────────────────────────────────────────────
# Payments & Revenue
# ──────────────────────────────────────────────────────────────────────────────
GARL_OWNER_EMAIL      = config('GARL_OWNER_EMAIL',      default='')
GARL_DEFAULT_CURRENCY = config('GARL_DEFAULT_CURRENCY', default='USD')
