from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ===========================================================
# SECURITY
# ===========================================================

# Keep this secret in production — never share it publicly
SECRET_KEY = 'django-insecure-vvw13@-@f9_$)fa8042aqop@3q563im3b%-dxqbk5882#)jv=_'

# Turn this off when deploying to production
DEBUG = True

# In production, replace with your actual domain e.g. ['commerce.com']
ALLOWED_HOSTS = []


# ===========================================================
# INSTALLED APPS
# corsheaders — allows React (localhost:5173) to talk to Django
# rest_framework — enables API views
# base — our main app
# ===========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',       # ✅ handles cross-origin requests from React
    'rest_framework',    # ✅ Django REST Framework for API views
    'base',              # ✅ our main app
]


# ===========================================================
# MIDDLEWARE
# CorsMiddleware MUST be at the very top
# It checks every incoming request and adds CORS headers
# so the browser allows React to receive the response
# ===========================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # ✅ must be FIRST
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'myproject.urls'


# ===========================================================
# TEMPLATES
# ===========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# ===========================================================
# DATABASE
# Using MySQL — make sure MySQL is running locally
# and ecommerce_db exists before running the server
# ===========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecommerce_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# ===========================================================
# PASSWORD VALIDATION
# These rules enforce strong passwords on registration
# ===========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ===========================================================
# INTERNATIONALISATION
# ===========================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ===========================================================
# STATIC FILES
# ===========================================================

STATIC_URL = 'static/'


# ===========================================================
# CUSTOM USER MODEL
# Tells Django to use our User model in base/models/users.py
# instead of the default Django user
# ===========================================================

AUTH_USER_MODEL = 'base.User'


# ===========================================================
# DJANGO REST FRAMEWORK
# Tells DRF to use JWT tokens for authentication
# So every protected API view checks the Bearer token
# ===========================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


# ===========================================================
# JWT SETTINGS
# access token lasts 60 minutes — after that user must refresh
# refresh token lasts 1 day — after that user must login again
# ===========================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}


# ===========================================================
# CORS SETTINGS
# This tells Django to accept requests from React
# running on localhost:5173 during development
# When deployed, replace with your real frontend domain
# ===========================================================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',   # ✅ React dev server
]

import os

# Where uploaded files are saved on disk
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL prefix for accessing uploaded files
# e.g. http://localhost:8000/media/products/image.jpg
MEDIA_URL = '/media/'