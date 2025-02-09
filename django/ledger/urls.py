from django.urls import path
from .views import (
    TransactionListCreateView, TransactionDetailView,
    CategoryListCreateView, CategoryDetailView,
    LedgerCalendarView, LedgerTransactionListView,
)

urlpatterns = [
    # 거래 내역 관련 URL
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<int:id>/', TransactionDetailView.as_view(), name='transaction-detail'),

    # 카테고리 관련 URL
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),

    path('ledger/<int:storeId>/calendar/', LedgerCalendarView.as_view(), name='ledger-calendar'),
    path('ledger/<int:storeId>/transactions/', LedgerTransactionListView.as_view(), name='ledger-transactions'),
]
