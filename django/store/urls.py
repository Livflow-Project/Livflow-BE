from django.urls import path
from .views import StoreView

urlpatterns = [
    # 가게 목록 조회 및 가게 등록
    path('stores/', StoreView.as_view(), name='store-list-create'),

    # 특정 가게 조회, 수정 및 삭제
    path('stores/<int:id>/', StoreView.as_view(), name='store-detail'),
]
