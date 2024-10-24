from django.urls import path
from .views import TransactionView, CategoryView

urlpatterns = [
    # 거래 내역 목록 조회 및 생성 엔드포인트 (GET: 목록 조회, POST: 새 거래 생성)
    path('transactions/', TransactionView.as_view(), name='transaction-list-create'),
    
    # 특정 거래 내역 조회, 수정 및 삭제 엔드포인트 (GET: 특정 거래 조회, PUT: 수정, DELETE: 삭제)
    path('transactions/<int:id>/', TransactionView.as_view({'get': 'get_detail', 'put': 'put', 'delete': 'delete'}), name='transaction-detail'),
    
    # 카테고리 목록 조회 및 생성 엔드포인트 (GET: 목록 조회, POST: 새 카테고리 생성)
    path('categories/', CategoryView.as_view(), name='category-list-create'),
    
    # 특정 카테고리 조회, 수정 및 삭제 엔드포인트 (GET: 특정 카테고리 조회, PUT: 수정, DELETE: 삭제)
    path('categories/<int:id>/', CategoryView.as_view({'get': 'get_detail', 'put': 'put', 'delete': 'delete'}), name='category-detail'),
]
