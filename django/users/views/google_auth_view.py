import os
import requests
import logging
from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.utils import store_refresh_token  
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken



# 로깅 설정
logger = logging.getLogger(__name__)

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class GoogleExchangeCodeForToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("🔍 Google OAuth 요청 시작")
        
        code = request.data.get("code")
        logger.info(f"📌 받은 Authorization Code: {code}")

        if not code:
            logger.error("❌ Authorization Code가 없습니다.")
            return JsonResponse({"error": "Authorization code is missing"}, status=400)

        token_endpoint = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }

        try:
            response = requests.post(token_endpoint, data=data, headers={"Accept": "application/x-www-form-urlencoded"})
            logger.info(f"📌 Google OAuth 응답 상태 코드: {response.status_code}")

            response.raise_for_status()
            token_data = response.json()
            logger.info(f"📌 Google OAuth Token Response: {token_data}")

            access_token = token_data.get("access_token")
            if not access_token:
                logger.error("❌ Google에서 Access Token을 가져오지 못했습니다.")
                return JsonResponse({"error": "Failed to obtain access token"}, status=400)

            userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(userinfo_endpoint, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            logger.info(f"📌 Google User Info Response: {user_info}")

            email = user_info.get("email")
            full_name = user_info.get("name", "").strip()

            if not email:
                logger.error("❌ Google User Info에 이메일 정보가 없습니다.")
                return JsonResponse({"error": "Email not found in user info"}, status=400)

            # ✅ 트랜잭션을 사용하여 User 및 SocialAccount 저장
            with transaction.atomic():
                user, created = User.objects.get_or_create(email=email, defaults={"first_name": full_name})
                logger.info(f"✅ User 정보: {user} (Created: {created})")

                # ✅ SocialAccount가 존재하지 않으면 생성
                social_account, social_created = SocialAccount.objects.get_or_create(
                    user=user,
                    provider="google",
                    defaults={"uid": email, "extra_data": user_info}
                )

                if social_created:
                    logger.info(f"✅ Google 소셜 계정 저장 완료: {user.email}")

            # ✅ JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token_obj = refresh.access_token
            access_token = str(access_token_obj)
            refresh_token = str(refresh)
            print("✅ JWT 토큰 생성 완료")

            # ✅ Redis에 Refresh Token 저장
            expires_in = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())  
            store_refresh_token(user.id, refresh_token, expires_in)
            print(f"✅ Redis에 Refresh Token 저장 완료 (Expires in: {expires_in}s)")
            
            # ✅ AccessToken 블랙리스트에 등록하기 위한 OutstandingToken 저장
            OutstandingToken.objects.get_or_create(
                jti=access_token_obj['jti'],
                defaults={
                    'user': user,
                    'token': access_token,
                    'expires_at': access_token_obj['exp'],
                }
            )

            # ✅ 응답 데이터 구성 (Bearer 방식)
            response_data = {
                "access": access_token,
                "refresh": refresh_token
            }
            return JsonResponse(response_data)


        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Google OAuth 요청 실패: {str(e)}")
            return JsonResponse({"error": f"Google OAuth Request Failed: {str(e)}"}, status=500)

        except Exception as e:
            logger.error(f"❌ 내부 서버 오류 발생: {str(e)}")
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)
