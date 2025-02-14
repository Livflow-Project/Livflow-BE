from django.urls import path
from .views import (
    StoreRecipeListView,
    StoreRecipeDetailView,
    StoreRecipeCreateView,
    StoreRecipeUpdateView,
    StoreRecipeDeleteView
)

urlpatterns = [
    path('costcalcul/<int:store_id>/', StoreRecipeListView.as_view(), name='store-recipe-list'),
    path('costcalcul/<int:store_id>/<int:recipe_id>/', StoreRecipeDetailView.as_view(), name='store-recipe-detail'),
    path('costcalcul/<int:store_id>/', StoreRecipeCreateView.as_view(), name='store-recipe-create'),
    path('costcalcul/<int:store_id>/<int:recipe_id>/', StoreRecipeUpdateView.as_view(), name='store-recipe-update'),
    path('costcalcul/<int:store_id>/<int:recipe_id>/', StoreRecipeDeleteView.as_view(), name='store-recipe-delete'),
]
