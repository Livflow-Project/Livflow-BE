from django.urls import path
from .views import StoreRecipeListView, StoreRecipeDetailView

urlpatterns = [
    path('<uuid:store_id>/', StoreRecipeListView.as_view(), name='store-recipes'),  # ✅ GET, POST
    path('<uuid:store_id>/<uuid:recipe_id>/', StoreRecipeDetailView.as_view(), name='recipe-detail'),  # ✅ GET, PUT, DELETE
]