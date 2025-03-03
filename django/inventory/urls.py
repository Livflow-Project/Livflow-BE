from django.urls import path
from .views import StoreInventoryView, UseIngredientStockView

urlpatterns = [
    path('<int:store_id>/', StoreInventoryView.as_view(), name='store-inventory'),  # ✅ 특정 상점의 전체 재고 조회
    path('<int:store_id>/<int:ingredient_id>/use/', UseIngredientStockView.as_view(), name='use-ingredient-stock'),  # ✅ 특정 재료 사용
]
