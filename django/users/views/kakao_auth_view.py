import os
import requests
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from users.utils import store_refresh_token  # Redis 저장 유틸리티 사용

User = get_user_model()

class KakaoExchangeCodeForToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        token_endpoint = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("KAKAO_CLIENT_ID"),
            "client_secret": os.getenv("KAKAO_CLIENT_SECRET"),  # ✅ 보안 강화
            "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
            "code": code,
        }

        try:
            # ✅ 토큰 요청
            response = requests.post(token_endpoint, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                return JsonResponse({"error": "Failed to obtain access token"}, status=400)

            # ✅ 사용자 정보 요청
            userinfo_endpoint = "https://kapi.kakao.com/v2/user/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(userinfo_endpoint, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()

            # ✅ 이메일 및 카카오 ID 추출
            kakao_account = user_info.get("kakao_account", {})
            email = kakao_account.get("email")
            kakao_id = str(user_info.get("id"))

            if not email:
                return JsonResponse({"error": "Email not found in user info"}, status=400)
            if not kakao_id:
                return JsonResponse({"error": "Kakao ID not found"}, status=400)

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
                domain=".livflow.co.kr",
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                samesite="Strict",
            )

            return response

        except Exception as e:
            # ✅ 에러 메시지 상세화
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)
