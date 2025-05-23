from django.urls import path

from .views.google_auth_view import GoogleExchangeCodeForToken
from .views.kakao_auth_view import KakaoExchangeCodeForToken
from .views.naver_auth_view import NaverExchangeCodeForToken
from .views.user_auth_view import (
    RefreshAccessTokenView,
    SocialLogout,
    UserTokenVerifyView,
    TestTokenView
)

urlpatterns = [
    # social login endpoint
    path("google/login/callback/", GoogleExchangeCodeForToken.as_view(), name="google_callback"),
    path("naver/login/callback/", NaverExchangeCodeForToken.as_view(), name="naver_callback"),
    path("kakao/login/callback/", KakaoExchangeCodeForToken.as_view(), name="kakao_callback"),
    path("logout/", SocialLogout.as_view(), name="logout"),
    # user_auth
    path("token/verify/", UserTokenVerifyView.as_view(), name="token-verify"),
    path("token/refresh/", RefreshAccessTokenView.as_view(), name="token_refresh"),
    path("test-token/", TestTokenView.as_view(), name="test-token"),
    ]