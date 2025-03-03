from django.contrib import admin
from .models import Ingredient

# ✅ 재료(Ingredient) 관리
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "store", "purchase_price", "purchase_quantity", "unit", "vendor")
    list_filter = ("store", "unit", "vendor")
    search_fields = ("name", "store__name")
    ordering = ("id",)
