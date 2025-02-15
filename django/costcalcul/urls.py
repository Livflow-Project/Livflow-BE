from django.urls import path
from .views import (
    StoreRecipeListView,
    StoreRecipeDetailView,
    StoreRecipeCreateView
)

urlpatterns = [
    # 특정 상점의 모든 레시피 조회 (GET), 레시피 생성 (POST)
    path('<int:store_id>/', StoreRecipeListView.as_view(), name='store-recipe-list-create'),

    # 특정 레시피 조회 (GET), 수정 (PUT), 삭제 (DELETE)
    path('<int:store_id>/<int:recipe_id>/', StoreRecipeDetailView.as_view(), name='store-recipe-detail'),
]
