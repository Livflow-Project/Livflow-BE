from django.urls import path
from .views import StoreInventoryView, IngredientDetailView

urlpatterns = [
    path('<uuid:store_id>/', StoreInventoryView.as_view(), name='store-ingredients'),  # ✅ UUID 적용
    path('<uuid:store_id>/<uuid:ingredient_id>/', IngredientDetailView.as_view(), name='ingredient-detail'),  # ✅ UUID 적용
]
