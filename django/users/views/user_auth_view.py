from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.conf import settings

from users.utils import (
    store_refresh_token,
    get_refresh_token,
    delete_refresh_token,
    verify_refresh_token
)

# ✅ 쿠키 기반 JWT 인증
class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 쿠키에서 액세스 토큰 가져오기
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if not raw_token:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            return None


# ✅ 토큰 유효성 검증 및 자동 갱신
class UserTokenVerifyView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        user_id = request.user.id

        if not access_token:
            return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # 액세스 토큰 검증
            AccessToken(access_token)
            return Response({"message": "Access token is valid"}, status=status.HTTP_200_OK)

        except (InvalidToken, TokenError):
            # 액세스 토큰이 만료된 경우, Redis에서 리프레시 토큰 확인
            stored_refresh_token = get_refresh_token(user_id)
            if not stored_refresh_token:
                return Response({"error": "Refresh token not found"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                # 리프레시 토큰 검증
                refresh = RefreshToken(stored_refresh_token)
                new_access_token = str(refresh.access_token)

                response = Response({
                    "message": "Access token was expired, but refresh token is valid",
                    "new_access_token": new_access_token,
                }, status=status.HTTP_200_OK)

                # 새로운 액세스 토큰을 쿠키에 설정
                response.set_cookie(
                    "access_token",
                    new_access_token,
                    max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                    httponly=True,
                    secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                    samesite="Strict",
                    domain=".livflow.co.kr",
                )
                return response

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
            response.set_cookie(
                "access_token",
                new_access_token,
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                httponly=True,
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite="Strict",
                domain=".livflow.co.kr",
            )
            return response

        except (InvalidToken, TokenError):
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# ✅ 소셜 로그아웃 (리프레시 토큰 삭제)
class SocialLogout(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id

        # Redis에서 리프레시 토큰 삭제
        delete_refresh_token(user_id)

        response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

        # 쿠키 삭제
        response.delete_cookie("access_token", domain=".livflow.co.kr", path="/")
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

# from rest_framework import status
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# from django.conf import settings

# from users.utils import (
#     store_refresh_token,
#     get_refresh_token,
#     delete_refresh_token,
#     verify_refresh_token
# )

# # ✅ 쿠키 기반 JWT 인증
# class CookieJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
#         if not raw_token:
#             return None
#         try:
#             validated_token = self.get_validated_token(raw_token)
#             return self.get_user(validated_token), validated_token
#         except (InvalidToken, TokenError):
#             return None


# # ✅ 토큰 유효성 검증 및 자동 갱신
# class UserTokenVerifyView(APIView):
#     authentication_classes = [CookieJWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         access_token = request.COOKIES.get("access_token")
#         user_id = request.user.id

#         if not access_token:
#             return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             AccessToken(access_token)
#             return Response({"message": "Access token is valid"}, status=status.HTTP_200_OK)

#         except (InvalidToken, TokenError):
#             stored_refresh_token = get_refresh_token(user_id)
#             if not stored_refresh_token:
#                 return Response({"error": "Refresh token not found"}, status=status.HTTP_401_UNAUTHORIZED)

#             try:
#                 refresh = RefreshToken(stored_refresh_token)
#                 new_access_token = str(refresh.access_token)

#                 response = Response({
#                     "message": "Access token was expired, but refresh token is valid",
#                     "new_access_token": new_access_token,
#                 }, status=status.HTTP_200_OK)

#                 # ✅ 로컬 환경 설정 적용
#                 response.set_cookie(
#                     "access_token",
#                     new_access_token,
#                     max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
#                     httponly=True,
#                     secure=False,  # ✅ 로컬에서는 HTTPS 없이 동작하도록 False
#                     samesite="Lax",  # ✅ 크로스 도메인 테스트를 위해 Lax
#                     domain=None,  # ✅ 로컬에서는 도메인 없이 설정 (자동 적용)
#                 )
#                 return response

#             except (InvalidToken, TokenError):
#                 return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# # ✅ 액세스 토큰 재발급
# class RefreshAccessTokenView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         refresh_token = request.data.get("refresh_token")

#         if not refresh_token:
#             return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             refresh = RefreshToken(refresh_token)
#             user_id = refresh.payload["user_id"]

#             if not verify_refresh_token(user_id, refresh_token):
#                 return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

#             new_access_token = str(refresh.access_token)

#             response = Response({"message": "Access token refreshed successfully"}, status=status.HTTP_200_OK)
#             response.set_cookie(
#                 "access_token",
#                 new_access_token,
#                 max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
#                 httponly=True,
#                 secure=False,  # ✅ 로컬에서는 HTTPS 없이 동작하도록 False
#                 samesite="Lax",  # ✅ 크로스 도메인 테스트를 위해 Lax
#                 domain=None,  # ✅ 로컬에서는 도메인 없이 설정 (자동 적용)
#             )
#             return response

#         except (InvalidToken, TokenError):
#             return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# # ✅ 소셜 로그아웃 (리프레시 토큰 삭제)
# class SocialLogout(APIView):
#     authentication_classes = [CookieJWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user_id = request.user.id

#         delete_refresh_token(user_id)

#         response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

#         response.delete_cookie("access_token")  # ✅ 로컬에서는 도메인 없이 삭제
#         return response
