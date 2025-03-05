from django.urls import path
from .views import StoreRecipeListView, StoreRecipeDetailView

urlpatterns = [
    path('<int:store_id>/', StoreRecipeListView.as_view(), name='store-recipes'),  # ✅ GET, POST
    path('<int:store_id>/<int:recipe_id>/', StoreRecipeDetailView.as_view(), name='recipe-detail'),  # ✅ GET, PUT, DELETE
]
