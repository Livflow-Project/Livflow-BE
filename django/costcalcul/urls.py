from django.urls import path
from .views import IngredientView, RecipeView

urlpatterns = [
    # 재료 관련 엔드포인트
    path('ingredients/', IngredientView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:id>/', IngredientView.as_view({'get': 'get_detail', 'put': 'put', 'delete': 'delete'}), name='ingredient-detail'),

    # 레시피 및 레시피 재료 관련 엔드포인트
    path('recipes/', RecipeView.as_view(), name='recipe-list-create'),
    path('recipes/<int:id>/', RecipeView.as_view({'get': 'get_detail', 'put': 'put', 'delete': 'delete'}), name='recipe-detail'),
    path('recipeitems/', RecipeView.as_view({'post': 'post_recipe_item', 'get': 'get_recipe_items'}), name='recipeitem-list-create'),
]
