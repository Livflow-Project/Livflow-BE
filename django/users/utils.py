import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True
)

def store_refresh_token(user_id, refresh_token, expires_in):
    """Redis에 리프레시 토큰 저장"""
    redis_client.setex(f"refresh_token:{user_id}", expires_in, refresh_token)

def get_refresh_token(user_id):
    """Redis에서 리프레시 토큰 조회"""
    return redis_client.get(f"refresh_token:{user_id}")

def delete_refresh_token(user_id):
    """Redis에서 리프레시 토큰 삭제 (로그아웃 시)"""
    redis_client.delete(f"refresh_token:{user_id}")
