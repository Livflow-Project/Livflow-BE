from rest_framework import serializers
from .models import Recipe, RecipeItem
from inventory.models import Inventory
from ingredients.models import Ingredient  # ✅ Ingredient 모델 추가
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .utils import calculate_recipe_cost


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
        ingredients_data = validated_data.pop('ingredients', [])  
        recipe = Recipe.objects.create(**validated_data)

        ingredient_costs = []  # ✅ 재료 원가 계산용 리스트

        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(Ingredient, id=ingredient_data["ingredient_id"])

            # ✅ Inventory 확인 후, 없으면 자동 생성
            inventory, created = Inventory.objects.get_or_create(
                ingredient=ingredient,
                defaults={"remaining_stock": ingredient.purchase_quantity}
            )

            required_amount = Decimal(str(ingredient_data.get("quantity_used", 0)))  # ✅ KeyError 방지

            # ✅ 사용량 차감 (재고가 충분한지 체크)
            if inventory.remaining_stock < required_amount:
                raise serializers.ValidationError(
                    f"{ingredient.name} 재고가 부족합니다. (남은 재고: {inventory.remaining_stock})"
                )

            inventory.remaining_stock -= required_amount  
            inventory.save()

            RecipeItem.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity_used=required_amount,
                unit=ingredient_data["unit"]
            )

            # ✅ ingredient_costs에 `unit_price` 추가
            ingredient_costs.append({
                "ingredient_id": str(ingredient.id),
                "ingredient_name": ingredient.name,
                "unit_price": float(ingredient.unit_cost or 0),  # ✅ `None` 방지
                "quantity_used": required_amount,
                "unit": ingredient_data["unit"]
            })

        # ✅ 레시피 원가 계산 함수 호출 시 `ingredient_costs` 전달
        cost_data = calculate_recipe_cost(
            ingredients=ingredient_costs,
            sales_price_per_item=recipe.sales_price_per_item,
            production_quantity_per_batch=recipe.production_quantity_per_batch
        )

        # ✅ `cost_data`를 recipe 객체에 추가하려면 필요함 (DB 저장은 안 되고 응답만 포함됨)
        recipe.total_ingredient_cost = cost_data["total_material_cost"]
        recipe.production_cost = cost_data["cost_per_item"]

        return recipe
