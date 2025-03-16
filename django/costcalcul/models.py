from django.db import models
from store.models import Store
import os
from uuid import uuid4
from decimal import Decimal


def recipe_image_upload_path(instance, filename):
    """이미지를 저장할 경로 설정"""
    ext = filename.split('.')[-1]
    new_filename = f"{uuid4().hex}.{ext}"
    return os.path.join("recipe_images", new_filename)


# 레시피(Recipe) 모델
class Recipe(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="recipes", default=1)
    name = models.CharField(max_length=255)
    sales_price_per_item = models.FloatField(null=True, blank=True)
    production_quantity_per_batch = models.IntegerField(default=1)
    recipe_img = models.ImageField(upload_to=recipe_image_upload_path, null=True, blank=True)  # ✅ 이미지 필드 추가
    is_favorites = models.BooleanField(default=False)
    
    total_ingredient_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 총 재료비
    production_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 개당 원가
    
    def __str__(self):
        return self.name

    @property
    def total_material_cost(self):
        return sum(item.material_cost for item in self.recipe_items.all()) if self.recipe_items.exists() else 0

    @property
    def material_cost_per_item(self):
        if self.production_quantity_per_batch and self.total_material_cost:
            return self.total_material_cost / self.production_quantity_per_batch
        return 0

    @property
    def cost_ratio(self):
        """ ✅ 원가 비율 계산 (Decimal 변환) """
        if self.sales_price_per_item and self.material_cost_per_item:
            return (self.material_cost_per_item / Decimal(self.sales_price_per_item)) * 100  # ✅ Decimal 변환
        return 0


# 레시피-재료 관계 모델 (RecipeItem)
class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_items', on_delete=models.CASCADE)
    ingredient = models.ForeignKey("ingredients.Ingredient", on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=2, choices=[('mg', 'Milligram'), ('ml', 'Milliliter'), ('ea', 'Each')])
    def __str__(self):
        return f"{self.ingredient.name} in {self.recipe.name}"

    @property
    def material_cost(self):
        """ ✅ 개별 재료 원가 계산 """
        if self.ingredient.unit_cost and self.quantity_used:
            return self.ingredient.unit_cost * self.quantity_used
        return 0

    @property
    def material_ratio(self):
        total_cost = self.recipe.total_material_cost
        if total_cost:
            return (self.material_cost / total_cost) * 100
        return 0
