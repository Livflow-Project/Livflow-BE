from django.urls import path
from .views import StoreInventoryView, UseIngredientStockView

urlpatterns = [
    path('<uuid:store_id>/', StoreInventoryView.as_view(), name='store-inventory'),
    path('<uuid:store_id>/<uuid:ingredient_id>/use/', UseIngredientStockView.as_view(), name='use-ingredient-stock'),
]
