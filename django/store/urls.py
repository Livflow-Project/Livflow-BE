from django.urls import path
from .views import StoreListView, StoreDetailView


urlpatterns = [
    path('', StoreListView.as_view(), name='store-list-create'),
    path('<uuid:id>/', StoreDetailView.as_view(), name='store-detail'),
]
