from django.contrib import admin
from .models import Ingredient
from inventory.models import Inventory  # ✅ Inventory 모델 추가

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "store", "purchase_price", "purchase_quantity", "unit", "vendor")
    list_filter = ("store", "unit", "vendor")
    search_fields = ("name", "store__name")
    ordering = ("id",)

    # ✅ Ingredient 저장 시 Inventory 자동 생성
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)  # ✅ 기본 저장 로직 실행
        
        # ✅ Inventory에 재료가 없으면 생성 (중복 방지)
        inventory, created = Inventory.objects.get_or_create(
            ingredient=obj,
            defaults={
                "remaining_stock": obj.purchase_quantity,  # ✅ 최초 구매량을 재고로 저장
                "unit": obj.unit,
                "unit_cost": obj.unit_cost,
            }
        )

        # ✅ 이미 존재하는 경우 (수정된 경우), 남은 재고 업데이트
        if not created:
            inventory.remaining_stock = obj.purchase_quantity
            inventory.unit_cost = obj.unit_cost
            inventory.save()
