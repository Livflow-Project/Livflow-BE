from rest_framework import serializers
from .models import Recipe, RecipeItem

# 레시피(Recipe) 시리얼라이저
class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'sales_price_per_item', 'production_quantity_per_batch']
        read_only_fields = ['id']

# 레시피 재료(RecipeItem) 시리얼라이저
class RecipeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeItem
        fields = ['id', 'recipe', 'ingredient', 'quantity_used', 'unit']
        read_only_fields = ['id']
