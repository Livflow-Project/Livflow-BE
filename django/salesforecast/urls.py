# salesforecast/urls.py

from django.urls import path
from .views import SalesPredictAPIView, MarketForecastAPIView

urlpatterns = [
    path("predict/", SalesPredictAPIView.as_view(), name="sales-predict"),
    path("market-predict/", MarketForecastAPIView.as_view(), name="market-predict"),
]
