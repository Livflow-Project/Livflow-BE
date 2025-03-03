from django.db import models
from store.models import Store  # 기존 store 앱의 Store 모델 가져오기

# ✅ 재료(Ingredient) 모델
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('mg', 'Milligram'),
        ('ml', 'Milliliter'),
        ('ea', 'Each'),
    ]

    store = models.ForeignKey(Store, related_name='ingredients', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=2, choices=UNIT_CHOICES)
    vendor = models.CharField(max_length=100, blank=True, null=True)  # 판매처 (shop)
    notes = models.TextField(blank=True, null=True)  # 기타 설명 (ingredient_detail)

    def __str__(self):
        return self.name

    @property
    def unit_cost(self):
        if self.purchase_quantity and self.purchase_price:
            return self.purchase_price / self.purchase_quantity
        return 0
