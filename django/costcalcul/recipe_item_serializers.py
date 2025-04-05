from rest_framework import serializers
from django.shortcuts import get_object_or_404
from ingredients.models import Ingredient  # ✅ Ingredient 모델 import
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
        """🚀 unit_price를 반환할 때 `dict` 타입이 아닌 모델 인스턴스를 사용하도록 수정"""
        if isinstance(obj, dict):  
            ingredient_id = obj.get("ingredient_id")
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)  # Ingredient 모델에서 가져오기
        else:
            ingredient = obj.ingredient  

        return ingredient.unit_cost
