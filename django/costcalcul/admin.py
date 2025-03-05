from django.contrib import admin
from django.utils.html import format_html
from .models import Recipe, RecipeItem

# ✅ 레시피(Recipe) 관리
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "store", "sales_price_per_item",
        "production_quantity_per_batch", "total_material_cost_display",
        "cost_ratio_display", "recipe_img_preview"  # ✅ 이미지 필드 미리보기로 변경
    )
    list_filter = ("store",)
    search_fields = ("name", "store__name")
    ordering = ("id",)

    # ✅ 총 원가(total_material_cost) 계산하여 표시
    def total_material_cost_display(self, obj):
        return f"{obj.total_material_cost:,.0f} 원" if obj.total_material_cost else "0 원"
    total_material_cost_display.short_description = "총 원가"

    # ✅ 원가 비율(cost_ratio) 계산하여 표시
    def cost_ratio_display(self, obj):
        return f"{obj.cost_ratio:.1f} %" if obj.cost_ratio else "0 %"
    cost_ratio_display.short_description = "원가 비율"

    # ✅ 이미지 필드 미리보기 추가
    def recipe_img_preview(self, obj):
        if obj.recipe_img:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;"/>', obj.recipe_img.url)
        return "No Image"
    recipe_img_preview.short_description = "이미지"

# ✅ 레시피-재료 관계(RecipeItem) 관리
@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "quantity_used", "unit", "material_cost_display")
    list_filter = ("recipe__store", "recipe", "ingredient")
    search_fields = ("recipe__name", "ingredient__name")
    ordering = ("id",)

    # ✅ 개별 재료 원가 계산하여 표시
    def material_cost_display(self, obj):
        return f"{obj.material_cost:,.0f} 원" if obj.material_cost else "0 원"
    material_cost_display.short_description = "개별 원가"
