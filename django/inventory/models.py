from django.db import models
from ingredients.models import Ingredient

class Inventory(models.Model):
    ingredient = models.OneToOneField(Ingredient, on_delete=models.CASCADE, related_name="inventory")  # ✅ 1:1 관계 (재료와 연결)
    remaining_stock = models.FloatField(default=0)  # ✅ 현재 남은 재고
    updated_at = models.DateTimeField(auto_now=True)  # ✅ 최근 업데이트 날짜

    def __str__(self):
        return f"{self.ingredient.name} - {self.remaining_stock} {self.ingredient.unit}"
