from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "get_store", "remaining_stock", "get_unit")  # ✅ store, unit 올바르게 가져오기
    search_fields = ("ingredient__name", "ingredient__store__name")  # ✅ store는 ingredient에서 가져와야 함
    list_filter = ("ingredient__store",)  # ✅ store 필터링 가능하게 수정

    def get_store(self, obj):
        return obj.ingredient.store.name  # ✅ store 정보 가져오기
    get_store.short_description = "Store"

    def get_unit(self, obj):
        return obj.ingredient.unit  # ✅ 단위 정보 가져오기
    get_unit.short_description = "Unit"
