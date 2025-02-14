from django.db import models

# 상점(Store) 모델 (상점별 관리 필요 시 추가)
class Store(models.Model):
    name = models.CharField(max_length=100)  # 상점 이름
    address = models.TextField(blank=True, null=True)  # 상점 주소

    def __str__(self):
        return self.name


# 재료(Ingredient) 모델
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('mg', 'Milligram'),
        ('ml', 'Milliliter'),
        ('ea', 'Each'),
    ]

    store = models.ForeignKey(Store, related_name='ingredients', on_delete=models.CASCADE)  # 상점과 연결
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
        return self.purchase_price / self.purchase_quantity if self.purchase_quantity else 0


# 원가 계산(Recipe) 및 재료(RecipeItem) 모델
class Recipe(models.Model):
    store = models.ForeignKey(Store, related_name='recipes', on_delete=models.CASCADE)  # 상점과 연결
    name = models.CharField(max_length=100)  # 메뉴 이름
    sales_price_per_item = models.DecimalField(max_digits=10, decimal_places=2)  # 개당 판매가
    production_quantity_per_batch = models.PositiveIntegerField()  # 1 배합 시 생산 수량
    recipe_img = models.CharField(max_length=255, blank=True, null=True)  # 레시피 이미지 (선택사항)

    def __str__(self):
        return self.name

    @property
    def total_material_cost(self):
        return sum(item.material_cost for item in self.recipe_items.all())

    @property
    def material_cost_per_item(self):
        return self.total_material_cost / self.production_quantity_per_batch if self.production_quantity_per_batch else 0

    @property
    def cost_ratio(self):
        return (self.material_cost_per_item / self.sales_price_per_item) * 100 if self.sales_price_per_item else 0


# 레시피-재료 관계 모델 (RecipeItem)
class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_items', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)  # 사용량
    unit = models.CharField(max_length=2, choices=Ingredient.UNIT_CHOICES)  # 단위

    def __str__(self):
        return f"{self.ingredient.name} in {self.recipe.name}"

    @property
    def material_cost(self):
        return self.ingredient.unit_cost * self.quantity_used

    @property
    def material_ratio(self):
        total_cost = self.recipe.total_material_cost
        return (self.material_cost / total_cost) * 100 if total_cost else 0
