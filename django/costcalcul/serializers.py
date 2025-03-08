from rest_framework import serializers
from .models import Recipe, RecipeItem
from ingredients.models import Ingredient  # ✅ Ingredient 모델 추가

# ✅ 레시피 재료(RecipeItem) 시리얼라이저 (Nested Serializer)
class RecipeItemSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.UUIDField(write_only=True)  # ✅ 프론트에서 ingredient_id만 받도록 설정
    required_amount = serializers.FloatField(source="quantity_used")  # ✅ 필드명 변환
    unit = serializers.CharField(required=True)
    
    class Meta:
        model = RecipeItem
        fields = ['id', 'ingredient_id', 'required_amount', 'unit']
        read_only_fields = ['id']

# ✅ 레시피(Recipe) 시리얼라이저
class RecipeSerializer(serializers.ModelSerializer):
    recipe_name = serializers.CharField(source="name")  # ✅ `recipe_name`을 `name`으로 매핑
    recipe_cost = serializers.FloatField(source="sales_price_per_item")  # ✅ `recipe_cost` → `sales_price_per_item` 변환
    recipe_img = serializers.ImageField(required=False)  # ✅ 선택값 처리
    ingredients = RecipeItemSerializer(many=True, write_only=True)  # ✅ Nested Serializer 추가
    production_quantity = serializers.IntegerField(source="production_quantity_per_batch")

    class Meta:
        model = Recipe
        fields = ['id', 'recipe_name', 'recipe_cost', 'recipe_img', 'is_favorites', 'ingredients', 'production_quantity']
        read_only_fields = ['id']
    
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
