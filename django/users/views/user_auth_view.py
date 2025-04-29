from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.tokens import AccessToken, TokenError

from users.utils import (
    store_refresh_token,
    get_refresh_token,
    delete_refresh_token,
    verify_refresh_token
)


class UserTokenVerifyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = request.user.id

        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Access token not found"}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = auth_header.split("Bearer ")[1]

        try:
            UntypedToken(access_token)
            return Response({"message": "Access token is valid"}, status=status.HTTP_200_OK)

        except (InvalidToken, TokenError):
            stored_refresh_token = get_refresh_token(user_id)
            if not stored_refresh_token:
                return Response({"error": "Refresh token not found"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                refresh = RefreshToken(stored_refresh_token)
                new_access_token = str(refresh.access_token)

                return Response({
                    "message": "Access token was expired, but refresh token is valid",
                    "new_access_token": new_access_token,
                }, status=status.HTTP_200_OK)

            except (InvalidToken, TokenError):
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)



# ✅ 액세스 토큰 재발급
class RefreshAccessTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 리프레시 토큰 검증
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload["user_id"]

            if not verify_refresh_token(user_id, refresh_token):
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

            # 새로운 액세스 토큰 발급
            new_access_token = str(refresh.access_token)

            response = Response({"message": "Access token refreshed successfully"}, status=status.HTTP_200_OK)
            # response.set_cookie(
            #     "access_token",
            #     new_access_token,
            #     max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
            #     httponly=True,
            #     secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            #     samesite="Strict",
            #     domain=".livflow.co.kr",
            # )
            return response

        except (InvalidToken, TokenError):
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

class SocialLogout(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id

        # ✅ Redis에서 리프레시 토큰 삭제
        delete_refresh_token(user_id)

        # ✅ 액세스 토큰 블랙리스트에 추가
        raw_token = None

        # 1. 쿠키에서 access_token 확인
        # raw_token = request.COOKIES.get("access_token")

        # 2. 없으면 Authorization 헤더에서 Bearer 토큰 확인
        # if not raw_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            raw_token = auth_header.split("Bearer ")[1]

        if raw_token:
            try:
                token = AccessToken(raw_token)
                jti = token['jti']
                outstanding_token = OutstandingToken.objects.get(jti=jti)
                BlacklistedToken.objects.get_or_create(token=outstanding_token)
                print("✅ 액세스 토큰 블랙리스트에 등록 완료")
            except Exception as e:
                print(f"❌ 블랙리스트 추가 실패: {e}")

        response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

        return response


    
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


User = get_user_model()

class TestTokenView(APIView):
    permission_classes = [AllowAny]  # ✅ 로그인 없이 접근 가능 (테스트용)

    def post(self, request):
        """테스트용 JWT 토큰 생성"""
        email = request.data.get("email", "testuser@example.com")  # ✅ 기본 이메일 설정 가능
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"first_name": "테스트", "last_name": "사용자"}  # ✅ CustomUser 모델에 맞게 필드 설정
        )

        refresh = RefreshToken.for_user(user)  # ✅ JWT 토큰 생성
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id
        })
