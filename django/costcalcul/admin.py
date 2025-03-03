from django.contrib import admin
from .models import Ingredient, Recipe, RecipeItem  # Store 제거


# 레시피(Recipe) 관리
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "store", "sales_price_per_item", "production_quantity_per_batch", "recipe_img")
    list_filter = ("store",)
    search_fields = ("name", "store__name")
    ordering = ("id",)


# 레시피-재료 관계(RecipeItem) 관리
@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "quantity_used", "unit")
    list_filter = ("recipe__store", "recipe", "ingredient")
    search_fields = ("recipe__name", "ingredient__name")
    ordering = ("id",)
