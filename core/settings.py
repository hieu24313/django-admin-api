from pathlib import Path
import os
from dotenv import load_dotenv
from typing import Any, Dict
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')[:-1]

CSRF_TRUSTED_ORIGINS = [
    'https://tok.cydeva.tech',
    'https://bucket.cydeva.tech',
    'http://localhost:3000'
]

INSTALLED_APPS = [
    "daphne",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "apps.user",
    "apps.general",
    "apps.conversation",
    "apps.discovery",
    "apps.notification",
    'apps.blog',
    'apps.friend',
    "rest_framework",
    "storages",
    'ckeditor_uploader',
    'ckeditor',
    'django.contrib.humanize',
    'celery',
    'corsheaders',
    'channels',
    'django_admin_inline_paginator',
    'silk'
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.user.auth.JWTAuthentication",
        # 'rest_framework.authentication.SessionAuthentication'
    ]
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    'silk.middleware.SilkyMiddleware',  # track and profiling API
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
]


ROOT_URLCONF = "core.urls"
LOGIN_REDIRECT_URL = '/'
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                'django.template.context_processors.static',
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = 'core.asgi.application'
AUTH_USER_MODEL = 'user.CustomUser'
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
USE_DB = os.getenv('USE_DB') == 'True'

if USE_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASS'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    os.environ.get('SOCKET_REDIS_URL')],
            },
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    os.environ.get('SOCKET_REDIS_URL')],
            },
        },
    }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('CACHE_REDIS_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "TIMEOUT": 60,
        }
    }
}
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
# DJANGO_REDIS_IGNORE_EXCEPTIONS = True

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale/')
]
LANGUAGE_CODE = 'vi'

LANGUAGES = [
    ('vi', _('Vietnamese')),
    ('en', 'English'),
]

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'width': '100%',
        'toolbar_Custom': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline',
             'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'], ['Source'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList'],
            ['Indent', 'Outdent'],
            ['Maximize'],
        ],
        'autoParagraph': False,
        'enterMode': 2,
    }
}

JAZZMIN_SETTINGS: Dict[str, Any] = {
    "site_title": "TOK Admin",
    "site_header": "TOK Admin",
    "site_footer": "TOK Admin",
    "site_logo_classes": None,
    "site_icon": "/jazzmin/img/tok.png",  # Đường dẫn đến logo của bạn
    "site_logo": "/jazzmin/img/tok.png",

    "login_logo_background": "/jazzmin/img/tok.png",
    "welcome_sign": "Chào mừng đến với trang web quản trị TOK",
    "dashboard_title": "Trang chủ",
    # Copyright on the footer
    "copyright": "Cydeva Technology Solutions",
    "development_version": False,
    "version": "",
    "icons": {
        "user": "fas fa-users",
        "user.CustomUser": "fas fa-users",

        "general.Report": "far fa-flag",
        "general.DefaultSetting": "fas fa-wrench",
        "general.AppConfig": "fas fa-wrench",

        "conversation.Room": "fas fa-comments",

        "notification.Notification": "fas fa-bell",

    },
    # "search_model": ["user.WorkInformation"],
    "topmenu_links": [

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "user", "name": "Cài đặt giá trị"},
    ],
    # "order_with_respect_to": ["apps.user.workinformation"],

    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "use_google_fonts_cdn": True,
    # "language_chooser": True,
    "hide_models": [
        "django_celery_beat.clockedschedule",
        "django_celery_beat.crontabschedule",
        "django_celery_beat.intervalschedule",
        "django_celery_beat.solarschedule",
        "django_celery_beat.periodictask",
        "auth.group",
        "user.WorkInformation",
        "user.CharacterInformation",
        "user.SearchInformation",
        "user.HobbyInformation",
        "user.CommunicateInformation",
        "user.OTP",
        "general.DefaultAvatar",
        "general.DevSetting",
        "general.FileUpload",
        "notification.UserDevice",
    ],
    "custom_links": {
        "books": [{
            "name": "Admin Setting",
            "url": "admin_setting",
            "icon": "fas fa-comments",
            "permissions": ["user", "general"]
        }]
    },
    # "order_with_respect_to": ["general", "user.WorkInformation", "user"],
    "ui_builder": {"extras": ["imagekit", "filer"]},
    "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-purple navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

if os.getenv('USE_MINIO') == 'True':
    STORAGES = {
        "default": {"BACKEND": 'storages.backends.s3boto3.S3Boto3Storage'},
        "staticfiles": {"BACKEND": 'storages.backends.s3boto3.S3Boto3Storage'},
    }

    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")
    AWS_STORAGE_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT")
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False

OTP_PROVIDER_ID = os.getenv('OTP_PROVIDER_ID')
ZALO_OTP_URL = os.getenv('ZALO_OTP_URL')

STRINGEE_APP_ID = os.getenv("STRINGEE_APP_ID")
STRINGEE_APP_SECRET = os.getenv("STRINGEE_APP_SECRET")

SILKY_PYTHON_PROFILER = True
SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True  # User must have permissions
SILKY_META = True
SILKY_HIDE_SENSITIVE = False

SILKY_EXPLAIN_FLAGS = {'format':'JSON', 'costs': True}


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_ALL_HEADERS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost',  # jest-dom test server
    'http://localhost:3000',  # react developement server
    'http://192.168.1.79:3000',
    'http://192.168.1.79',
    'http://192.168.1.55:3000',
    'http://192.168.1.55',
    'https://django-bolt.vercel.app',
    'https://django-bolt-git-main-andev916s-projects.vercel.app'
]

CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://192.168.1.79:3000', 'http://192.168.1.79:3000',
                        'http://192.168.1.55:3000',
                        'http://192.168.1.55', 'https://django-bolt.vercel.app',
                        'https://django-bolt-git-main-andev916s-projects.vercel.app']

CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://192.168.1.79:3000', 'http://192.168.1.79:3000', 'http://192.168.1.55:3000',
                        'http://192.168.1.55', 'https://django-bolt.vercel.app', 'https://django-bolt-git-main-andev916s-projects.vercel.app', 'https://django-bolt.vercel.app/login']

# CSRF_COOKIE_DOMAIN = '.vercel.app'
# SESSION_COOKIE_DOMAIN = '.vercel.app'
# SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = None
CSRF_COOKIE_NAME = 'csrftoken'
# CSRF_COOKIE_HTTPONLY = True
# CSRF_USE_SESSIONS = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False  # Không yêu cầu cookie CSRF phải được gửi qua HTTPS

# CSRF_COOKIE_DOMAIN = 'localhost'  # Đặt tên miền cookie CSRF là 'localhost'
# SESSION_COOKIE_DOMAIN = 'localhost'
# CSRF_COOKIE_SECURE = False