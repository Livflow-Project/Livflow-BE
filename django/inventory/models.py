from django.db import models
from ingredients.models import Ingredient

class Inventory(models.Model):
    ingredient = models.OneToOneField(Ingredient, on_delete=models.CASCADE, related_name="inventory")
    remaining_stock = models.FloatField(default=0)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.ingredient.name} - {self.remaining_stock} {self.ingredient.unit}"

    @property
    def get_unit(self):
        """ ✅ Ingredient 모델에서 unit 가져오기 """
        return self.ingredient.unit

    @property
    def get_unit_cost(self):
        """ ✅ Ingredient 모델에서 unit_cost 가져오기 """
        return self.ingredient.unit_cost  # ✅ Ingredient에서 계산된 unit_cost 가져오기
