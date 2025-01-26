from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.conf import settings
from django.middleware import csrf

from users.utils import get_refresh_token
from users.utils import delete_refresh_token


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


class UserTokenVerifyView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 쿠키에서 액세스 토큰과 리프레시 토큰 가져오기
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token:
            return Response({"error": "Access token not found in cookies"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 액세스 토큰 검증
            AccessToken(access_token)
            return Response({"message": "Access token is valid"}, status=status.HTTP_200_OK)
        except (InvalidToken, TokenError):
            # 액세스 토큰이 유효하지 않을 경우
            if not refresh_token:
                return Response({"error": "Refresh token not found in cookies"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # 리프레시 토큰 검증
                refresh = RefreshToken(refresh_token)
                # 새로운 액세스 토큰 생성
                new_access_token = refresh.access_token
                response_data = {
                    "message": "Access token was expired, but refresh token is valid",
                    "new_access_token": str(new_access_token),
                }

                # 새로운 액세스 토큰을 쿠키에 설정
                response = Response(response_data, status=status.HTTP_200_OK)
                response.set_cookie("access_token", str(new_access_token), httponly=True, secure=True)
                return response

            except (InvalidToken, TokenError):
                # 리프레시 토큰이 유효하지 않을 경우
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class RefreshAccessTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.data.get("refresh_token")  # 요청 바디에서 가져옴

        if not refresh_token:
            return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)

            # Redis에서 저장된 리프레시 토큰 가져오기
            stored_refresh_token = get_refresh_token(refresh.payload["user_id"])
            if not stored_refresh_token or stored_refresh_token != refresh_token:
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

            # 새 액세스 토큰 발급
            new_access_token = str(refresh.access_token)
            response = Response({"message": "Access token refreshed successfully"}, status=status.HTTP_200_OK)
            response.set_cookie(
                "access_token",
                new_access_token,
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                httponly=True,
                samesite="Strict",
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                domain=".livflow.co.kr",
            )
            return response

        except (InvalidToken, TokenError):
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class SocialLogout(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Redis에서 리프레시 토큰 삭제
        delete_refresh_token(user.id)

        response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

        # 쿠키 삭제
        response.delete_cookie("access_token", domain=".livflow.co.kr", path="/")
        return response