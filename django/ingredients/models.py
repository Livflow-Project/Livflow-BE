import uuid
from django.db import models
from store.models import Store  
from django.utils.timezone import now 

# ✅ 재료(Ingredient) 모델
class Ingredient(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)  # ✅ UUID 사용
    store = models.ForeignKey(Store, related_name='ingredients', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ ingredient_cost
    purchase_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ capacity
    unit = models.CharField(max_length=2, choices=[
        ('g', 'gram'),
        ('ml', 'Milliliter'),
        ('ea', 'Each'),
    ])
    vendor = models.CharField(max_length=100, blank=True, null=True)  # ✅ shop
    notes = models.TextField(blank=True, null=True)  # ✅ ingredient_detail
    original_stock_before_edit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=now, editable=False)
    
    def __str__(self):
        return self.name

    @property
    def unit_cost(self):
        """ ✅ 단가 계산 """
        if self.purchase_quantity and self.purchase_price:
            return self.purchase_price / self.purchase_quantity
        return 0
