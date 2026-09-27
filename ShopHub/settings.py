"""
Django settings for ShopHub project.

Production-style e-commerce configuration.
"""

from pathlib import Path
import os

# ─────────────────────────────────────────────
# BASE DIRECTORY
# ─────────────────────────────────────────────
# BASE_DIR points to the root of the project (where manage.py lives).
BASE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────
# Keep the secret key secret in production (use environment variable).
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-shophub-dev-key-change-in-production-xyz123'
)

# Never run with DEBUG=True in production.
DEBUG = True

# In production, add your domain e.g. ['shophub.com', 'www.shophub.com']
ALLOWED_HOSTS = ['*']


# ─────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────
# Django built-ins first, then third-party, then our own apps.
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',   # for number formatting in templates

    # ShopHub custom apps
    'core',        # Homepage, about, contact, etc.
    'accounts',    # User registration, login, profile
    'products',    # Product listings, categories, search
    'cart',        # Shopping cart (session-based)
    'orders',      # Order placement and tracking
    'reviews',     # Product ratings and reviews
    'coupons',     # Discount codes and promotions
    'dashboard',      # Seller / admin analytics dashboard
    'notifications',  # In-app notification system
]

# ─────────────────────────────────────────────────────────
# CUSTOM USER MODEL
# ─────────────────────────────────────────────────────────
# Tell Django to use our CustomUser instead of the default User.
# This MUST be set before running the first migration.
AUTH_USER_MODEL = 'accounts.CustomUser'


# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ShopHub.urls'


# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────
# All HTML templates live in the project-level 'templates/' folder.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Point to the project-level templates directory
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,   # Also look inside each app's templates/ subfolder
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom context processor — makes cart count available site-wide
                'core.context_processors.cart_item_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'ShopHub.wsgi.application'


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
# SQLite is perfect for development. Swap for PostgreSQL in production.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────────
# AUTHENTICATION REDIRECTS
# ─────────────────────────────────────────────
# Where to send users after login / logout
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# ─────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────────
# STATIC FILES  (CSS, JavaScript, fonts, icons)
# ─────────────────────────────────────────────
# URL prefix used in templates: {% static 'css/style.css' %}
STATIC_URL = '/static/'

# Project-level static files folder (our CSS / JS / images)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Where `collectstatic` gathers all static files for production deployment
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ─────────────────────────────────────────────
# MEDIA FILES  (user-uploaded images, etc.)
# ─────────────────────────────────────────────
# URL prefix for uploaded files: /media/products/image.jpg
MEDIA_URL = '/media/'

# Filesystem path where uploads are saved
MEDIA_ROOT = BASE_DIR / 'static' / 'media'


# ─────────────────────────────────────────────
# DEFAULT PRIMARY KEY FIELD
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────────
# SESSION (used by cart app)
# ─────────────────────────────────────────────
# Store session data in the database (most reliable option)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session expires when the browser closes (can change to seconds, e.g. 86400)
SESSION_COOKIE_AGE = 86400  # 24 hours


# ─────────────────────────────────────────────
# EMAIL (Development: print to console)
# ─────────────────────────────────────────────
# In development we print emails to the terminal instead of sending them.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For production, switch to SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = 'noreply@shophub.com'


# ─────────────────────────────────────────────
# MESSAGES FRAMEWORK (flash messages)
# ─────────────────────────────────────────────
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG:   'secondary',
    messages.INFO:    'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR:   'danger',   # Bootstrap uses 'danger' not 'error'
}
