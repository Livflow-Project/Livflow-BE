from rest_framework import serializers
from .models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    # ✅ unit_cost 필드를 read-only로 추가 (가격/용량 자동 계산)
    unit_cost = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "purchase_price",
            "purchase_quantity",
            "unit",
            "unit_cost",
            "vendor",
            "notes",
            "store"
        ]
        read_only_fields = ["unit_cost", "store"]  # store 필드는 요청에서 수정 불가

    # ✅ unit_cost 자동 계산 (purchase_price / purchase_quantity)
    def get_unit_cost(self, obj):
        return obj.unit_cost if obj.unit_cost else 0
