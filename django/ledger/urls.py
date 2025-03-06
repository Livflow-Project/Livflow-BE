from django.urls import path
from .views import (
    LedgerTransactionListCreateView, LedgerTransactionDetailView,
    CategoryListCreateView, CategoryDetailView,
    LedgerCalendarView, LedgerDailyTransactionView
)

urlpatterns = [
    # ✅ `store_id`를 `uuid`로 변경
    path('<uuid:store_id>/transactions/', LedgerTransactionListCreateView.as_view(), name='ledger-transaction-list-create'),
    path('<uuid:store_id>/transactions/<uuid:transaction_id>/', LedgerTransactionDetailView.as_view(), name='ledger-transaction-detail'),

    path('<uuid:store_id>/calendar/', LedgerCalendarView.as_view(), name='ledger-calendar'),  # ✅ 수정됨
    path('<uuid:store_id>/transactions/daily/', LedgerDailyTransactionView.as_view(), name='ledger-daily-transactions'),  # ✅ 수정됨

    # 카테고리 관련 URL (기존 유지)
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
]
