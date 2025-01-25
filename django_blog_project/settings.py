"""
Django settings for django_blog_project project.
"""

from pathlib import Path
from datetime import timedelta
import os
import sys
import environ
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Development/Production switch
IS_DEVELOPMENT = 'dev' in sys.prefix.lower()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('S_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = IS_DEVELOPMENT

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    'TOKEN_USER_CLASS': 'django.contrib.auth.models.User',

    # Custom settings for development/production
    'AUTH_COOKIE': 'access_token',  # Cookie name for JWT
    'AUTH_COOKIE_SECURE': not IS_DEVELOPMENT,  # True in production
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_PATH': '/',
    'AUTH_COOKIE_SAMESITE': 'Lax',
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',   
    'blog.apps.BlogConfig',
    'users.apps.UsersConfig',
    'crispy_bootstrap4',
    'crispy_forms',
    'storages',
    'corsheaders',
    'django_extensions',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'social_django',
]

# Rest Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'users.authentication.CustomJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'blog.api.throttling.PostAPIThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/day',
    },
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'blog.api.exception_handlers.custom_exception_handler',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django_blog_project.middleware.CORSMiddleware',
    'django_blog_project.middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.RateLimitMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'django_blog_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "blog" / "templates",
            BASE_DIR / "users" / "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

# Social Auth Pipeline
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'users.pipeline.require_email_valaidation',                        
)

# Social Auth settings


# Social Auth Settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'prompt': 'select_account'
}

# Verify URLs match Google Console settings
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'blog-home'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/landing_page/'

# Security settings
SOCIAL_AUTH_REDIRECT_IS_HTTPS = not IS_DEVELOPMENT
SOCIAL_AUTH_SANITIZE_REDIRECTS = True
SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS = ['echoe5.com', 'www.echoe5.com', 'localhost', '127.0.0.1']

SOCIAL_AUTH_SANITIZE_REDIRECTS = True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = not IS_DEVELOPMENT



# Wsgi
WSGI_APPLICATION = 'django_blog_project.wsgi.application'

# Development Settings
if IS_DEVELOPMENT:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    
    # Security settings are relaxed for development
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    
    # Email verification toggle for development
    REQUIRE_EMAIL_VERIFICATION = False
    
    # Social Auth settings
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
    
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]
    
    # Development Installed Apps
    INSTALLED_APPS += [
        'management.apps.ManagementConfig',
    ]
    
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]
    
    # Development logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': str(BASE_DIR / 'logs/django.log'),
            },
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
        },
        'loggers': {
            'django.contrib.staticfiles': {
                'handlers': ['console'],
                'level': 'DEBUG',   
            }
        }
    }
    
    # Development email backend prints to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    # Development database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }
    
    # Static and Media files configuration for development
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [
        BASE_DIR / 'blog' / 'static',
    ]
    
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    
    # Development storage configuration
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Production Settings
else:
    ALLOWED_HOSTS = ['www.echoe5.com', 'echoe5.com']

    # Production security settings
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 Year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    
    # Email verification toggle for production
    REQUIRE_EMAIL_VERIFICATION = True
    
    # Production CORS settings
    CORS_ALLOWED_ORIGINS = [
        'https://echoe5.com',
        'https://www.echoe5.com',
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
    CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours
    
    # Production database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }
    
    CORS_ALLOWED_ORIGINS = [
        'https://echoe5.com',
        'https://www.echoe5.com',
    ]
    CORS_ALLOW_CREDENTIALS = True

    # Production email settings
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env('EMAIL_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_PASS')
    
    # Production static files configuration
    STATIC_ROOT = BASE_DIR / "staticfiles"
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    
    # Production storage configuration
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "location": "static"
            }
        },
    }
    
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Crispy Forms settings
CRISPY_ALLOWED_TEMPLATE_PACK = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Login settings
LOGIN_REDIRECT_URL = 'blog-home'
LOGIN_URL = 'login'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'