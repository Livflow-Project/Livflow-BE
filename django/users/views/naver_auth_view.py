import os
import requests
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from users.utils import store_refresh_token  # Redis에 토큰 저장

User = get_user_model()

class NaverExchangeCodeForToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")
        token_endpoint = "https://nid.naver.com/oauth2.0/token"

        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("NAVER_CLIENT_ID"),
            "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
            "code": code,
            "state": state,
        }

        try:
            # ✅ 액세스 토큰 요청
            response = requests.post(token_endpoint, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                return JsonResponse({"error": "Failed to obtain access token"}, status=400)

            # ✅ 사용자 정보 요청
            userinfo_endpoint = "https://openapi.naver.com/v1/nid/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(userinfo_endpoint, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json().get("response", {})

            # ✅ 이메일 확인
            email = user_info.get("email")
            if not email:
                return JsonResponse({"error": "Email not found in user info"}, status=400)

            # ✅ 사용자 생성 또는 가져오기
            user, created = User.objects.get_or_create(email=email)

            # ✅ JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # ✅ Redis에 리프레시 토큰 저장
            store_refresh_token(
                user.id,
                refresh_token,
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
            )

            response_data = {
                "access": access_token,
            }
            response = JsonResponse(response_data)

            # ✅ 액세스 토큰을 쿠키에 저장
            response.set_cookie(
                "access_token",
                access_token,
                domain=".livflow.co.kr",  # 도메인 수정
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                samesite="Strict",
            )

            return response

        except Exception as e:
            # ✅ 에러 메시지 상세화
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)
