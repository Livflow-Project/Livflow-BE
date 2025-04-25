import redis
import hashlib
from django.conf import settings

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

# ✅ 토큰 해싱 함수 (SHA-256)
def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

# ✅ 리프레시 토큰 저장 (해싱 후 저장)
def store_refresh_token(user_id, refresh_token, expires_in):
    """Redis에 해시된 리프레시 토큰 저장"""
    hashed_token = hash_token(refresh_token)
    redis_client.setex(f"refresh_token:{user_id}", int(expires_in), hashed_token)  


# ✅ 리프레시 토큰 조회 (해시된 토큰 반환)
def get_refresh_token(user_id):
    """Redis에서 해시된 리프레시 토큰 조회"""
    return redis_client.get(f"refresh_token:{user_id}")

# ✅ 리프레시 토큰 삭제
def delete_refresh_token(user_id):
    """Redis에서 리프레시 토큰 삭제 (로그아웃 시)"""
    redis_client.delete(f"refresh_token:{user_id}")

def verify_refresh_token(user_id, provided_token):
    """Redis에 저장된 해시와 비교하여 검증. 불일치 시 자동 삭제"""
    stored_hashed_token = get_refresh_token(user_id)
    hashed_provided_token = hash_token(provided_token)

    if stored_hashed_token != hashed_provided_token:
        # 불일치 → 탈취 가능성 → 삭제
        delete_refresh_token(user_id)
        return False

    return True

