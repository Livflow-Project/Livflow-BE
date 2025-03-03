from rest_framework import serializers
from .models import Inventory

class InventorySerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(source='ingredient.unit', read_only=True)
    unit_cost = serializers.FloatField(source='ingredient.unit_cost', read_only=True)  # ✅ 단가 추가

    class Meta:
        model = Inventory
        fields = ['ingredient', 'ingredient_name', 'remaining_stock', 'unit', 'unit_cost']
