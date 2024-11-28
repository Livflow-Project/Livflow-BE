from django.urls import path
from .views import StoreListView, StoreDetailView

urlpatterns = [
    # 가게 목록 조회 및 새 가게 등록 엔드포인트 (GET: 목록 조회, POST: 새 가게 등록)
    path('stores/', StoreListView.as_view(), name='store-list-create'),

    # 특정 가게 조회, 수정 및 삭제 엔드포인트 (GET: 특정 가게 조회, PUT: 수정, DELETE: 삭제)
    path('stores/<int:id>/', StoreDetailView.as_view(), name='store-detail'),
]
