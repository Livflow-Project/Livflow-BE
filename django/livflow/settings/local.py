from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ✅ SQLite 사용 (로컬 테스트)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}

# ✅ CORS 설정 (로컬 개발)
CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경에서는 모든 오리진 허용

# ✅ CSRF 예외 설정 (로컬 개발)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
]

# ✅ HTTPS 보안 설정 해제 (로컬 환경)
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
