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
class NaverExchangeCodeForToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("🔍 Naver OAuth 요청 시작")
        
        code = request.data.get("code")
        state = request.data.get("state")
        logger.info(f"📌 받은 Authorization Code: {code}, State: {state}")

        if not code or not state:
            logger.error("❌ Authorization Code 또는 State 값이 없습니다.")
            return JsonResponse({"error": "Authorization code or state is missing"}, status=400)

        token_endpoint = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("NAVER_CLIENT_ID"),
            "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
            "code": code,
            "state": state,
        }

        try:
            # ✅ Naver에서 액세스 토큰 요청
            response = requests.post(token_endpoint, data=data)
            logger.info(f"📌 Naver OAuth 응답 상태 코드: {response.status_code}")

            response.raise_for_status()
            token_data = response.json()
            logger.info(f"📌 Naver OAuth Token Response: {token_data}")

            access_token = token_data.get("access_token")
            if not access_token:
                logger.error("❌ Naver에서 Access Token을 가져오지 못했습니다.")
                return JsonResponse({"error": "Failed to obtain access token"}, status=400)

            # ✅ Naver에서 유저 정보 가져오기
            userinfo_endpoint = "https://openapi.naver.com/v1/nid/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(userinfo_endpoint, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json().get("response", {})
            logger.info(f"📌 Naver User Info Response: {user_info}")

            email = user_info.get("email")
            full_name = user_info.get("name", "").strip()

            if not email:
                logger.error("❌ Naver User Info에 이메일 정보가 없습니다.")
                return JsonResponse({"error": "Email not found in user info"}, status=400)

            # ✅ 이메일 기준으로 사용자 생성 또는 가져오기
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"first_name": full_name}
            )
            logger.info(f"✅ User 정보: {user} (Created: {created})")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            logger.info("✅ JWT 토큰 생성 완료")

            expires_in = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())  
            store_refresh_token(user.id, refresh_token, expires_in)
            logger.info(f"✅ Redis에 Refresh Token 저장 완료 (Expires in: {expires_in}s)")

            response_data = {"access": access_token}
            response = JsonResponse(response_data)

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
            logger.error(f"❌ Naver OAuth 요청 실패: {str(e)}")
            return JsonResponse({"error": f"Naver OAuth Request Failed: {str(e)}"}, status=500)

        except Exception as e:
            logger.error(f"❌ 내부 서버 오류 발생: {str(e)}")
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)
