import os
import requests
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()

# 카카오 소셜 로그인
class KakaoExchangeCodeForToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        token_endpoint = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("KAKAO_CLIENT_ID"),
            "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
            "code": code,
        }

        try:
            response = requests.post(token_endpoint, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                return JsonResponse({"error": "Failed to obtain access token"}, status=400)

            userinfo_endpoint = "https://kapi.kakao.com/v2/user/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(userinfo_endpoint, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()

            # 고유한 식별자로 카카오 ID를 사용
            kakao_id = str(user_info.get("id"))
            if not kakao_id:
                return JsonResponse({"error": "Kakao ID not found"}, status=400)

            # 이메일만 사용
            email = user_info.get("email")
            if not email:
                return JsonResponse({"error": "Email not found in user info"}, status=400)

            # 사용자 생성 또는 가져오기
            user, created = User.objects.get_or_create(email=email)

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            response_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            # 응답에 쿠키 설정
            response = JsonResponse(response_data)
            response.set_cookie(
                "refresh_token",
                str(refresh),
                domain=".livflow.co.kr",
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                max_age=6060247,
                samesite="Strict",
            )
            response.set_cookie(
                "access_token",
                str(refresh.access_token),
                domain=".livflow.co.kr",
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                max_age=6060247,
                samesite="Strict",
            )

            return response

        except Exception as e:
            # 토큰 교환 또는 사용자 정보 가져오기 오류 처리
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)
