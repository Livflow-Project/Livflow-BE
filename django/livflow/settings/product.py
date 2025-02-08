from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
from django.utils.translation import gettext

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-=f57%wq3lx)q4i6efhnbt!(7d567@nf6ifms9ib18n!0x-(_pz')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['api.livflow.co.kr', 'www.livflow.co.kr', 'localhost', '127.0.0.1','localhost:5173']

# Application definition
DEFAULT_DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

CUSTOM_INSTALLED_APPS = [
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',
    'rest_framework.authtoken',
    'rest_framework',
    'drf_yasg',
    'django_cleanup.apps.CleanupConfig',
    'ledger',
    'users',
    'costcalcul',
    'store',
]

INSTALLED_APPS = DEFAULT_DJANGO_APPS + CUSTOM_INSTALLED_APPS

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'livflow.urls'
WSGI_APPLICATION = 'livflow.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Redis
# REDIS_HOST = "localhost"
# REDIS_PORT = 6379
# REDIS_DB = 0


REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Docker 컨테이너에서는 "redis"
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))  # 기본 DB 인덱스


# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://www.livflow.co.kr",
    "https://api.livflow.co.kr",
    "https://api.livflow.co.kr:8443",
    "http://localhost:5173",
    "http://localhost:8000",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "x-csrftoken",
    "x-requested-with",
]


CSRF_TRUSTED_ORIGINS = [
    "https://www.livflow.co.kr",
    "https://api.livflow.co.kr",
    "https://api.livflow.co.kr:8443",
    "http://localhost:5173",
    "http://localhost:8000",
]

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = True # 배포용
# CSRF_COOKIE_SECURE = False # 개발용
SESSION_COOKIE_SECURE = True # 배포용
# SESSION_COOKIE_SECURE = False  # 개발용
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Social login settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "key": os.getenv("GOOGLE_SOCIAL_KEY"),
        }
    },
    "naver": {
        "APP": {
            "client_id": os.getenv("NAVER_CLIENT_ID"),
            "secret": os.getenv("NAVER_CLIENT_SECRET"),
            "key": os.getenv("NAVER_SOCIAL_KEY"),
        }
    },
    "kakao": {
        "APP": {
            "client_id": os.getenv("KAKAO_CLIENT_ID"),
            "secret": os.getenv("KAKAO_CLIENT_SECRET"),
            "key": os.getenv("KAKAO_SOCIAL_KEY"),
        }
    },
}

# JWT Authentication settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=int(os.getenv("ACCESS_TOKEN_LIFETIME_DAYS", 1))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", 7))),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_COOKIE": "access_token",
    "AUTH_COOKIE_SECURE": True,
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_PATH": "/",
    # "AUTH_COOKIE_SAMESITE": "Strict", # 배포용
    "AUTH_COOKIE_SAMESITE" : "Lax", # 개발용
    
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {},
    'loggers': {},
}
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         # 'file': {
#         #     'level': 'ERROR',
#         #     'class': 'logging.FileHandler',
#         #     'filename': os.path.join(BASE_DIR, 'logs', 'django_error.log'),  # 경로를 BASE_DIR 기준으로 설정
#         #     'formatter': 'verbose',
#         # },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     },
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
