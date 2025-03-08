# serializers.py
from rest_framework import serializers
from .models import Ingredient
from .utils import calculate_unit_price  # ✅ utils.py의 함수 불러오기

class IngredientSerializer(serializers.ModelSerializer):
    unit_cost = serializers.SerializerMethodField()
    ingredient_name = serializers.CharField(source="name")  # ✅ 필드명 매칭
    ingredient_cost = serializers.DecimalField(source="purchase_price", max_digits=10, decimal_places=2)
    capacity = serializers.DecimalField(source="purchase_quantity", max_digits=10, decimal_places=2)
    shop = serializers.CharField(source="vendor", required=False, allow_null=True)
    ingredient_detail = serializers.CharField(source="notes", required=False, allow_null=True)

    class Meta:
        model = Ingredient
        fields = [
            "id", "ingredient_name", "ingredient_cost", "capacity",
            "unit", "unit_cost", "shop", "ingredient_detail", "store"
        ]
        read_only_fields = ["unit_cost", "store"]

    # ✅ 단가 계산 함수 활용
    def get_unit_cost(self, obj):
        return calculate_unit_price(obj.purchase_price, obj.purchase_quantity)


