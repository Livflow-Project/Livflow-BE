# serializers.py
from rest_framework import serializers
from .models import Ingredient
from .utils import calculate_unit_price  # ✅ 여기서 불러와 활용

class IngredientSerializer(serializers.ModelSerializer):
    unit_cost = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = [
            "id", "name", "purchase_price", "purchase_quantity",
            "unit", "unit_cost", "vendor", "notes", "store"
        ]
        read_only_fields = ["unit_cost", "store"]

    # ✅ 단가(unit_cost) 계산
    def get_unit_cost(self, obj):
        return calculate_unit_price(obj.purchase_price, obj.purchase_quantity)
