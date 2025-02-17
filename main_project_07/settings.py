"""
Django settings for main_project_07 project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv  # .env 불러오기

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
if not load_dotenv():
    raise ValueError("❌ ERROR: .env file not found or could not be loaded!")

# 필수 환경 변수 로드
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("❌ ERROR: SECRET_KEY is not set in the environment variables!")

DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Debugging용 환경 변수 출력 (DEBUG 모드일 때만)
if DEBUG:
    print("🔍 DEBUG:", DEBUG)
    print("🔍 DB_NAME:", os.getenv("DB_NAME"))
    print("🔍 DB_USER:", os.getenv("DB_USER"))
    print("🔍 DB_HOST:", os.getenv("DB_HOST"))
    print("🔍 DB_PORT:", os.getenv("DB_PORT"))

# Application definition
DJANGO_SYSTEM_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]
CUSTOM_USER_APPS = [
    'diet',
    'user',
    'food',
    'common',
    'dietfood',
    'rest_framework',
    'rest_framework_simplejwt',
]

INSTALLED_APPS = DJANGO_SYSTEM_APPS + CUSTOM_USER_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main_project_07.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'main_project_07.wsgi.application'


# **📌 DB 설정 (Docker 또는 로컬 환경 감지)**
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST") if os.getenv("RUNNING_IN_DOCKER") else "localhost",
        'PORT': os.getenv("DB_PORT"),
    }
}



# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = []


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',  # ✅ JSON 응답만 반환
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'user.authentication.CookieJWTAuthentication',  # ✅ JWT 토큰을 쿠키에서 가져오는 인증 방식 추가
    ),
}



CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",  # 로컬 메모리 캐싱
        "LOCATION": "unique-snowflake",  # 캐시 구분을 위한 위치명
    }
}

AUTH_USER_MODEL = 'user.User'

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

import os

# Gunicorn 타임아웃 설정
os.environ.setdefault("GUNICORN_CMD_ARGS", "--timeout 60")

KAKAO_CLIENT_ID = "072d2d003b490b28d2f4e683471df7b8"
KAKAO_REDIRECT_URI = "http://localhost:3000/callback"
KAKAO_CLIENT_SECRET = ""  # 선택사항 (없어도 됨)

