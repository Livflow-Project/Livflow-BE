from django.urls import path
from .views import StoreListView, StoreDetailView
from .views import TestTokenView

urlpatterns = [
    path('', StoreListView.as_view(), name='store-list-create'),
    path('<uuid:id>/', StoreDetailView.as_view(), name='store-detail'),
    path("test-token/", TestTokenView.as_view(), name="test-token"),
]
