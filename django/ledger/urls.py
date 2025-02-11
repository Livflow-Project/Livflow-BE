from django.urls import path
from .views import (
    LedgerTransactionListCreateView, LedgerTransactionDetailView,
    CategoryListCreateView, CategoryDetailView
)

urlpatterns = [
    # 거래 내역 목록 조회 & 생성 (쿼리 파라미터로 특정 날짜 필터링 가능)
    path('ledger/<int:store_id>/transactions/', LedgerTransactionListCreateView.as_view(), name='ledger-transaction-list-create'),
    path('ledger/<int:store_id>/transactions/<uuid:transaction_id>/', LedgerTransactionDetailView.as_view(), name='ledger-transaction-detail'),

    # 카테고리 관련 URL
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
]
