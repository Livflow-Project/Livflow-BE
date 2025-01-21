from django.urls import path
from .views import (
    StoreListView, StoreDetailView, StoreCalendarView, 
    TransactionCreateView, TransactionDetailView
)

urlpatterns = [
    path('', StoreListView.as_view(), name='store-list-create'),
    path('<uuid:id>/', StoreDetailView.as_view(), name='store-detail'),
    path('<uuid:id>/calendar/', StoreCalendarView.as_view(), name='store-calendar'),
    path('<uuid:id>/transactions/', TransactionCreateView.as_view(), name='transaction-create'),
    path('<uuid:id>/transactions/<uuid:transaction_id>/', TransactionDetailView.as_view(), name='transaction-detail'),
]
