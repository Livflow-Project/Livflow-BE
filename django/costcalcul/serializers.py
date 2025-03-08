from rest_framework import serializers
from .models import Recipe, RecipeItem
from ingredients.models import Ingredient  # ✅ Ingredient 모델 추가

# ✅ 레시피 재료(RecipeItem) 시리얼라이저 (Nested Serializer)
class RecipeItemSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.UUIDField(write_only=True)  # ✅ 프론트에서 ingredient_id만 받도록 수정

    class Meta:
        model = RecipeItem
        fields = ['id', 'ingredient_id', 'quantity_used', 'unit']
        read_only_fields = ['id']

# ✅ 레시피(Recipe) 시리얼라이저
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeItemSerializer(many=True, write_only=True)  # ✅ Nested Serializer 추가

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'sales_price_per_item', 'production_quantity_per_batch', "recipe_img", "ingredients"]
        read_only_fields = ['id']
        recipe_img = serializers.ImageField(required=False)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])  # ✅ 재료 리스트 추출
        recipe = Recipe.objects.create(**validated_data)

        # ✅ 재료 등록
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data["ingredient_id"])
            RecipeItem.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity_used=ingredient_data["quantity_used"],
                unit=ingredient_data["unit"]
            )

        return recipe
