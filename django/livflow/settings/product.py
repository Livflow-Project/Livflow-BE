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
# CORS_ALLOW_ALL_ORIGINS = True # 배포시 False
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
#배포시 주석풀기
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

# Security settings(배포용)
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

#(로컬용)
# # ✅ 개발 환경에서는 HTTPS 보안 설정 비활성화
# SECURE_SSL_REDIRECT = False  
# SECURE_HSTS_SECONDS = 0  
# SECURE_HSTS_INCLUDE_SUBDOMAINS = False  
# SECURE_HSTS_PRELOAD = False  

# # ✅ CSRF & 쿠키 보안 완화 (로컬 개발용)
# CSRF_COOKIE_SECURE = False  
# SESSION_COOKIE_SECURE = False  

# # ✅ XSS 및 기타 보안 설정은 유지
# X_FRAME_OPTIONS = 'DENY'
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True


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
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # ✅ JWT 인증 활성화
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # ✅ 인증된 사용자만 접근 가능
    ],
}


# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.AllowAny',  # ✅ 인증 없이 모든 API 사용 가능
#     ],
# }

SPECTACULAR_SETTINGS = {
    'TITLE': 'Livflow API',
    'DESCRIPTION': 'Livflow 가계부, 단가계산기 API 입니다.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,  # ✅ 인증 유지 (Swagger 재시작 후에도 유지됨)
    },
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Enter token with "Bearer " prefix, e.g., Bearer <your_token>',
        }
    },
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
ACCOUNT_AUTHENTICATION_METHOD = "email"  # 로그인 시 email 사용
ACCOUNT_USERNAME_REQUIRED = False  # username 필드 사용 안 함
ACCOUNT_EMAIL_REQUIRED = True  # email 필수
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # ✅ username 필드 비활성화




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
