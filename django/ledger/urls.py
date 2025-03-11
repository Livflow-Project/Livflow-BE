from django.urls import path
from .views import (
    LedgerTransactionListCreateView, LedgerTransactionDetailView,
    CategoryListCreateView, CategoryDetailView,
    LedgerCalendarView
)

urlpatterns = [
    # 🔹 거래 내역 관련 API
    path('<uuid:store_id>/transactions/', LedgerTransactionListCreateView.as_view(), name='ledger-transaction-list-create'),
    path('<uuid:store_id>/transactions/<uuid:transaction_id>/', LedgerTransactionDetailView.as_view(), name='ledger-transaction-detail'),

    # 🔹 캘린더 및 일별 거래 조회 API
    path('<uuid:store_id>/calendar/', LedgerCalendarView.as_view(), name='ledger-calendar'),

    # 🔹 카테고리 관련 API
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<uuid:category_id>/', CategoryDetailView.as_view(), name='category-detail'),
]
