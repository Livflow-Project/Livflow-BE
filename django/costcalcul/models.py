from django.db import models

# 재료(Ingredient) 모델
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('mg', 'Milligram'),
        ('ml', 'Milliliter'),
        ('ea', 'Each'),
    ]

    name = models.CharField(max_length=100)  # 품목명
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  # 구매 가격
    purchase_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # 구매 용량
    unit = models.CharField(max_length=2, choices=UNIT_CHOICES)  # 단위 (mg, ml, ea)
    vendor = models.CharField(max_length=100, blank=True, null=True)  # 판매처 (선택사항)
    notes = models.TextField(blank=True, null=True)  # 비고 (선택사항)

    def __str__(self):
        return self.name

    @property
    def unit_cost(self):
        # 1단위당 단가 계산: 구매 가격 / 구매 용량
        return self.purchase_price / self.purchase_quantity


# 원가 계산(Recipe) 및 재료(RecipeItem) 모델
class Recipe(models.Model):
    name = models.CharField(max_length=100)  # 메뉴 이름
    sales_price_per_item = models.DecimalField(max_digits=10, decimal_places=2)  # 개당 판매가
    production_quantity_per_batch = models.PositiveIntegerField()  # 1 배합 시 생산 수량

    def __str__(self):
        return self.name

    # 총재료 원가 계산
    @property
    def total_material_cost(self):
        total_cost = sum(item.material_cost for item in self.recipe_items.all())
        return total_cost

    # 1개당 재료 원가 계산
    @property
    def material_cost_per_item(self):
        return self.total_material_cost / self.production_quantity_per_batch

    # 원가 비율 계산
    @property
    def cost_ratio(self):
        if self.sales_price_per_item > 0:
            return (self.material_cost_per_item / self.sales_price_per_item) * 100
        return 0


class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_items', on_delete=models.CASCADE)  # 메뉴와 연결
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)  # 재료
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)  # 사용량
    unit = models.CharField(max_length=2, choices=Ingredient.UNIT_CHOICES)  # 단위

    def __str__(self):
        return f"{self.ingredient.name} in {self.recipe.name}"

    # 재료당 원가 계산 (단가 * 사용량)
    @property
    def material_cost(self):
        return self.ingredient.unit_cost * self.quantity_used

    # 재료 비율 계산 (재료당 원가 / 총재료 원가)
    @property
    def material_ratio(self):
        total_cost = self.recipe.total_material_cost
        if total_cost > 0:
            return (self.material_cost / total_cost) * 100
        return 0
