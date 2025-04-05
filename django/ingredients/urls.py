from django.urls import path
from .views import StoreIngredientView, IngredientDetailView, IngredientUsagesView

urlpatterns = [
    path('<uuid:store_id>/', StoreIngredientView.as_view(), name='store-ingredients'),  
    path('<uuid:store_id>/<uuid:ingredient_id>/', IngredientDetailView.as_view(), name='ingredient-detail'), 
    path('<uuid:store_id>/<uuid:ingredient_id>/usages/', IngredientUsagesView.as_view(), name='ingredient-usages'),
]
