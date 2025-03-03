from django.urls import path
from .views import (
    StoreRecipeListView,
    StoreRecipeDetailView,
    StoreRecipeCreateView,
    StoreInventoryView, IngredientCreateView, UseIngredientStockView
)

urlpatterns = [
    # 특정 상점의 모든 레시피 조회 (GET), 레시피 생성 (POST)
    path('<int:store_id>/', StoreRecipeListView.as_view(), name='store-recipe-list-create'),

    # 특정 레시피 조회 (GET), 수정 (PUT), 삭제 (DELETE)
    path('<int:store_id>/<int:recipe_id>/', StoreRecipeDetailView.as_view(), name='store-recipe-detail'),
    
        # 특정 상점의 모든 재료 및 재고 조회
    path('inventory/<int:store_id>/', StoreInventoryView.as_view(), name='store-inventory'),

    # 특정 상점의 재료 추가 (초기 재고 설정)
    path('ingredients/<int:store_id>/', IngredientCreateView.as_view(), name='ingredient-create'),

    # 특정 재료 사용 (재고 감소)

    path('inventory/<int:store_id>/<int:ingredient_id>/use/', UseIngredientStockView.as_view(), name='use-ingredient-stock'),

]


