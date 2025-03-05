from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "get_store", "remaining_stock", "get_unit", "get_received_stock", "get_used_stock")  
    search_fields = ("ingredient__name", "ingredient__store__name")  
    list_filter = ("ingredient__store",)  
    ordering = ("id",)

    # ✅ 수정 가능 필드 지정 (received_stock, used_stock 제거)
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

    def get_received_stock(self, obj):
        """✅ 입고량을 보여주는 가상 필드 (예제 값, 실제 필드 없음)"""
        return "수동 입력 필요"
    get_received_stock.short_description = "입고량"

    def get_used_stock(self, obj):
        """✅ 사용량을 보여주는 가상 필드 (예제 값, 실제 필드 없음)"""
        return "수동 입력 필요"
    get_used_stock.short_description = "사용량"
