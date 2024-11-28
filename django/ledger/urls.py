from django.urls import path
from .views import (
    IngredientListView,
    IngredientDetailView,
    RecipeListView,
    RecipeDetailView,
    RecipeItemCreateView,
    RecipeItemListView
)

urlpatterns = [
    # 재료 목록 조회 및 생성 엔드포인트 (GET: 목록 조회, POST: 새 재료 생성)
    path('ingredients/', IngredientListView.as_view(), name='ingredient-list-create'),

    # 특정 재료 조회, 수정 및 삭제 엔드포인트 (GET: 특정 재료 조회, PUT: 수정, DELETE: 삭제)
    path('ingredients/<int:id>/', IngredientDetailView.as_view(), name='ingredient-detail'),

    # 레시피 목록 조회 및 생성 엔드포인트 (GET: 목록 조회, POST: 새 레시피 생성)
    path('recipes/', RecipeListView.as_view(), name='recipe-list-create'),

    # 특정 레시피 조회, 수정 및 삭제 엔드포인트 (GET: 특정 레시피 조회, PUT: 수정, DELETE: 삭제)
    path('recipes/<int:id>/', RecipeDetailView.as_view(), name='recipe-detail'),

    # 레시피 재료 생성 엔드포인트 (POST: 새 레시피 재료 생성)
    path('recipe-items/', RecipeItemCreateView.as_view(), name='recipe-item-create'),

    # 레시피 재료 목록 조회 엔드포인트 (GET: 목록 조회)
    path('recipe-items/list/', RecipeItemListView.as_view(), name='recipe-item-list'),
]
