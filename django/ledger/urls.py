from django.urls import path
from .views import (
    TransactionListCreateView, TransactionDetailView,
    CategoryListCreateView, CategoryDetailView,
    LedgerCalendarView, LedgerTransactionListView,
)

urlpatterns = [
    # 거래 내역 관련 URL (store_id 포함)
    path('<int:store_id>/transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('<int:store_id>/transactions/<int:id>/', TransactionDetailView.as_view(), name='transaction-detail'),

    # 카테고리 관련 URL
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),

    # 가게별 차트 및 거래 내역 조회
    path('<int:store_id>/calendar/', LedgerCalendarView.as_view(), name='ledger-calendar'),
    path('<int:store_id>/transactions/daily/', LedgerTransactionListView.as_view(), name='ledger-transactions'),
]
