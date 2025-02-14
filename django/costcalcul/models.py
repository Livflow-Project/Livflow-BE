from django.db import models
from store.models import Store  # 기존 store 앱에서 Store 모델 가져오기

# 재료(Ingredient) 모델
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('mg', 'Milligram'),
        ('ml', 'Milliliter'),
        ('ea', 'Each'),
    ]

    store = models.ForeignKey(Store, related_name='ingredients', on_delete=models.CASCADE, null=True, blank=True)  # store 앱의 Store 모델 참조
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


# 레시피(Recipe) 모델
class Recipe(models.Model):
    store = models.ForeignKey(Store, related_name='recipes', on_delete=models.CASCADE, null=True, blank=True)  # store 앱의 Store 모델 참조
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
