from rest_framework import serializers
from .models import RecipeItem

# ✅ 레시피 재료(RecipeItem) 시리얼라이저
class RecipeItemSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.UUIDField(write_only=True)
    required_amount = serializers.DecimalField(source="quantity_used", max_digits=10, decimal_places=2)  
    unit_price = serializers.SerializerMethodField()  

    class Meta:
        model = RecipeItem
        fields = ['id', 'ingredient_id', 'required_amount', 'unit_price']
        read_only_fields = ['id']

    def get_unit_price(self, obj):
        """✅ Ingredient의 unit_cost를 unit_price로 변환"""
        return float(obj.ingredient.unit_cost) if obj.ingredient else 0
