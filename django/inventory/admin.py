from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "get_store", "remaining_stock", "received_stock", "used_stock", "get_unit")  
    search_fields = ("ingredient__name", "ingredient__store__name")  
    list_filter = ("ingredient__store",)  
    ordering = ("id",)

    # ✅ 수정 가능 필드 지정 (store, unit 제거)
    fields = ("ingredient", "received_stock", "used_stock", "remaining_stock")

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

    # ✅ 저장할 때 재고 자동 계산
    def save_model(self, request, obj, form, change):
        # 기존 재고 불러오기 (없으면 0으로 설정)
        old_stock = Inventory.objects.filter(id=obj.id).first()
        previous_stock = old_stock.remaining_stock if old_stock else 0

        # `received_stock`과 `used_stock`이 None일 경우 0으로 처리하여 오류 방지
        received_stock = obj.received_stock if obj.received_stock else 0
        used_stock = obj.used_stock if obj.used_stock else 0

        # 새로운 재고 계산 (기존 재고 + 입고량 - 사용량)
        obj.remaining_stock = previous_stock + received_stock - used_stock

        super().save_model(request, obj, form, change)
