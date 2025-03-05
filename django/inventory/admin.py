from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "get_store", "remaining_stock", "get_unit")  # ✅ 불필요한 필드 제거
    search_fields = ("ingredient__name", "ingredient__store__name")  
    list_filter = ("ingredient__store",)  
    ordering = ("id",)

    # ✅ 수정 가능 필드 지정
    fields = ("ingredient", "remaining_stock")

    # ✅ 읽기 전용 필드 (remaining_stock 자동 계산)
    readonly_fields = ("remaining_stock",)

    def get_store(self, obj):
        """✅ Ingredient 모델에서 store 가져오기"""
        return obj.ingredient.store.name if obj.ingredient.store else "No Store"
    get_store.short_description = "Store"

    def get_unit(self, obj):
        """✅ Ingredient 모델에서 unit 가져오기"""
        return obj.ingredient.unit if obj.ingredient.unit else "No Unit"
    get_unit.short_description = "Unit"
