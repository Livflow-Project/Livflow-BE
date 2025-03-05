from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "get_store", "remaining_stock", "get_unit", "get_unit_cost")  
    search_fields = ("ingredient__name", "ingredient__store__name")  
    list_filter = ("ingredient__store",)  
    ordering = ("id",)

    # ✅ 수정 가능 필드 지정
    fields = ("ingredient", "remaining_stock")

    # ✅ 읽기 전용 필드
    readonly_fields = ("remaining_stock",)

    def get_store(self, obj):
        """ ✅ Ingredient 모델에서 store 가져오기 """
        return obj.ingredient.store.name if obj.ingredient.store else "No Store"
    get_store.short_description = "Store"

    def get_unit(self, obj):
        """ ✅ Ingredient 모델에서 unit 가져오기 """
        return obj.get_unit  
    get_unit.short_description = "Unit"

    def get_unit_cost(self, obj):
        """ ✅ Ingredient 모델에서 unit_cost 가져오기 """
        return f"{obj.get_unit_cost:.2f} 원"
    get_unit_cost.short_description = "단가 (unit cost)"
