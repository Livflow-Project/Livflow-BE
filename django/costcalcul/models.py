from django.db import models
from store.models import Store

# ✅ Ingredient 모델 삭제 (이미 ingredients 앱에서 관리됨)

# 레시피(Recipe) 모델
class Recipe(models.Model):
    store = models.ForeignKey(Store, related_name='recipes', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    sales_price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    production_quantity_per_batch = models.PositiveIntegerField()
    recipe_img = models.CharField(max_length=255, blank=True, null=True)

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
        if self.sales_price_per_item and self.material_cost_per_item:
            return (self.material_cost_per_item / self.sales_price_per_item) * 100
        return 0


# 레시피-재료 관계 모델 (RecipeItem)
class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_items', on_delete=models.CASCADE)
    ingredient = models.ForeignKey("ingredients.Ingredient", on_delete=models.CASCADE)  # ✅ ingredients 앱의 Ingredient를 참조하도록 수정
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=2, choices=[('mg', 'Milligram'), ('ml', 'Milliliter'), ('ea', 'Each')])

    def __str__(self):
        return f"{self.ingredient.name} in {self.recipe.name}"

    @property
    def material_cost(self):
        if self.ingredient.unit_cost is not None and self.quantity_used is not None:
            return self.ingredient.unit_cost * self.quantity_used
        return 0

    @property
    def material_ratio(self):
        total_cost = self.recipe.total_material_cost
        if total_cost:
            return (self.material_cost / total_cost) * 100
        return 0
