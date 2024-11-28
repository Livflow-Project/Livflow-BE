from django.urls import path
from .views import StoreListView, StoreDetailView

urlpatterns = [
    # 모든 가게 목록 조회 및 새로운 가게 등록
    path('stores/', StoreListView.as_view(), name='store-list'),
    
    # 특정 가게 조회, 수정 및 삭제
    path('stores/<int:id>/', StoreDetailView.as_view(), name='store-detail'),
]
