import os
import requests
import logging
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.utils import store_refresh_token  

# 로깅 설정
logger = logging.getLogger(__name__)

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class GoogleExchangeCodeForToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("🔍 Google OAuth 요청 시작")
        
        # 1️⃣ ✅ 요청에서 `code` 확인
        code = request.data.get("code")
        logger.info(f"📌 받은 Authorization Code: {code}")

        if not code:
            logger.error("❌ Authorization Code가 없습니다.")
            return JsonResponse({"error": "Authorization code is missing"}, status=400)

        token_endpoint = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": "191567703208-tp56ppl7hokenh12v8pibctruiapqm9j.apps.googleusercontent.com",
            "client_secret": "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",
            "redirect_uri": "https://www.livflow.co.kr/auth/login/callback/google",
            "grant_type": "authorization_code",
        }

        try:
            # 2️⃣ ✅ Google OAuth 서버에 요청
            logger.info("🛰️ Google OAuth 서버에 토큰 요청 중...")
            response = requests.post(token_endpoint, data=data, headers={"Accept": "application/x-www-form-urlencoded"})
            logger.info(f"📌 Google OAuth 응답 상태 코드: {response.status_code}")

            response.raise_for_status()  # ❌ 여기서 오류 발생 가능!
            token_data = response.json()
            logger.info(f"📌 Google OAuth Token Response: {token_data}")

            # 3️⃣ ✅ Access Token 획득
            access_token = token_data.get("access_token")
            if not access_token:
                logger.error("❌ Google에서 Access Token을 가져오지 못했습니다.")
                return JsonResponse({"error": "Failed to obtain access token"}, status=400)

            # 4️⃣ ✅ 유저 정보 요청
            userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(userinfo_endpoint, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            logger.info(f"📌 Google User Info Response: {user_info}")

            # 5️⃣ ✅ 이메일 확인
            email = user_info.get("email")
            if not email:
                logger.error("❌ Google User Info에 이메일 정보가 없습니다.")
                return JsonResponse({"error": "Email not found in user info"}, status=400)

            # 6️⃣ ✅ 유저 생성 또는 가져오기
            user, created = User.objects.get_or_create(email=email)
            logger.info(f"✅ User 정보: {user} (Created: {created})")

            # 7️⃣ ✅ JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            logger.info("✅ JWT 토큰 생성 완료")

            # 8️⃣ ✅ Redis에 Refresh Token 저장
            try:
                expires_in = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())  
                store_refresh_token(user.id, refresh_token, expires_in)
                logger.info(f"✅ Redis에 Refresh Token 저장 완료 (Expires in: {expires_in}s)")
            except Exception as e:
                logger.error(f"❌ Redis 저장 중 오류 발생: {str(e)}")

            response_data = {
                "access": access_token,
            }
            response = JsonResponse(response_data)

            # 9️⃣ ✅ 쿠키 설정
            response.set_cookie(
                "access_token",
                access_token,
                domain=".livflow.co.kr",
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
                samesite="Strict",
            )
            logger.info("✅ 액세스 토큰을 쿠키에 저장 완료")

            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Google OAuth 요청 실패: {str(e)}")
            return JsonResponse({"error": f"Google OAuth Request Failed: {str(e)}"}, status=500)

        except Exception as e:
            logger.error(f"❌ 내부 서버 오류 발생: {str(e)}")
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)
