from django.urls import path
from .views import (
    IngredientListView, IngredientDetailView,
    RecipeListView, RecipeDetailView,
    RecipeItemCreateView, RecipeItemListView
)

urlpatterns = [
    # 재료 관련 엔드포인트
    path('ingredients/', IngredientListView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:id>/', IngredientDetailView.as_view(), name='ingredient-detail'),

    # 레시피 관련 엔드포인트
    path('recipes/', RecipeListView.as_view(), name='recipe-list-create'),
    path('recipes/<int:id>/', RecipeDetailView.as_view(), name='recipe-detail'),

    # 레시피 재료 관련 엔드포인트
    path('recipeitems/', RecipeItemCreateView.as_view(), name='recipeitem-create'),
    path('recipeitems/list/', RecipeItemListView.as_view(), name='recipeitem-list'),
]
