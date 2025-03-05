from django.contrib import admin
from .models import Ingredient

# ✅ 재료(Ingredient) 관리
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "store", "purchase_price", "purchase_quantity", "unit", "unit_cost_display", "vendor")
    list_filter = ("store", "unit", "vendor")
    search_fields = ("name", "store__name")
    ordering = ("id",)

    def unit_cost_display(self, obj):
        """ ✅ Django Admin에서 단가(unit_cost) 표시 (DB 저장 X) """
        return round(obj.unit_cost, 2)  # 소수점 2자리까지 표시
    unit_cost_display.short_description = "단가 (unit cost)"  # Admin 컬럼 제목
