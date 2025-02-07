import os
import requests
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from users.utils import store_refresh_token  # utils.py에서 가져오기
from datetime import timedelta


User = get_user_model()

class GoogleExchangeCodeForToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        token_endpoint = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": "191567703208-tp56ppl7hokenh12v8pibctruiapqm9j.apps.googleusercontent.com",
            "client_secret": "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",
            "redirect_uri": "http://localhost:5173/auth/login/callback/google",
            # "code": code,
            # "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            # "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            # "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }

        try:
            response = requests.post(token_endpoint, data=data, headers={"Accept": "application/x-www-form-urlencoded"})
            response.raise_for_status()
            token_data = response.json()

            access_token = token_data.get("access_token")
            if not access_token:
                return JsonResponse({"error": "Failed to obtain access token"}, status=400)

            # 유저 정보 요청
            userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(userinfo_endpoint, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()

            email = user_info.get("email")
            if not email:
                return JsonResponse({"error": "Email not found in user info"}, status=400)

            user, created = User.objects.get_or_create(email=email)

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Redis에 리프레시 토큰 저장
            expires_in = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())  # ✅ 정수로 변환
            store_refresh_token(user.id, refresh_token, expires_in)

            response_data = {
                "access": access_token,
            }
            response = JsonResponse(response_data)

            # 액세스 토큰을 쿠키에 저장
            response.set_cookie(
                "access_token",
                access_token,
                domain=".livflow.co.kr",
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),  # ✅ 정수로 변환
                samesite="Strict",
            )

            return response

        except Exception as e:
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)