from django.urls import path
from .views import (
    StoreInventoryView,  # ✅ GET, POST 함께 처리
    IngredientDetailView,
)

urlpatterns = [
    path('<int:store_id>/', StoreInventoryView.as_view(), name='store-ingredients'),  # ✅ GET & POST
    path('<int:store_id>/<int:ingredient_id>/', IngredientDetailView.as_view(), name='ingredient-detail'),  # ✅ GET, PUT, DELETE
]
