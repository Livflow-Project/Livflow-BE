from django.urls import path
from .views import StoreInventoryView, UseIngredientStockView

urlpatterns = [
    path('<int:store_id>/', StoreInventoryView.as_view(), name='store-inventory'),
    path('<int:store_id>/<int:ingredient_id>/use/', UseIngredientStockView.as_view(), name='use-ingredient-stock'),
]
