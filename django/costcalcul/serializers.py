from rest_framework import serializers
from .models import Recipe, RecipeItem
from inventory.models import Inventory
from ingredients.models import Ingredient  
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .utils import calculate_recipe_cost
import logging

logger = logging.getLogger(__name__)

# ✅ 레시피 재료(RecipeItem) 시리얼라이저 (Nested Serializer)
class RecipeItemSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.UUIDField(write_only=True)
    required_amount = serializers.DecimalField(source="quantity_used", max_digits=10, decimal_places=2)  
    unit = serializers.CharField(required=True)
    unit_price = serializers.SerializerMethodField()  # ✅ unit_price 추가

    class Meta:
        model = RecipeItem
        fields = ['id', 'ingredient_id', 'required_amount', 'unit', 'unit_price']
        read_only_fields = ['id']

    def get_unit_price(self, obj):
        """✅ Ingredient의 unit_cost를 unit_price로 변환"""
        return float(obj.ingredient.unit_cost) if obj.ingredient else 0


# ✅ 레시피(Recipe) 시리얼라이저
class RecipeSerializer(serializers.ModelSerializer):
    recipe_name = serializers.CharField(source="name")
    recipe_cost = serializers.DecimalField(source="sales_price_per_item", max_digits=10, decimal_places=2)
    recipe_img = serializers.ImageField(required=False)
    ingredients = RecipeItemSerializer(many=True, write_only=True)  
    production_quantity = serializers.IntegerField(source="production_quantity_per_batch")

    # ✅ 추가 필드 (응답에 포함되지만 DB에는 저장되지 않음)
    total_ingredient_cost = serializers.SerializerMethodField()
    production_cost = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'recipe_name', 'recipe_cost', 'recipe_img', 'is_favorites', 'ingredients', 'production_quantity', 'total_ingredient_cost', 'production_cost']
        read_only_fields = ['id']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])  
        recipe = Recipe.objects.create(**validated_data)

        ingredient_costs = []  

        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(Ingredient, id=ingredient_data["ingredient_id"])

            inventory, created = Inventory.objects.get_or_create(
                ingredient=ingredient,
                defaults={"remaining_stock": ingredient.purchase_quantity}
            )

            # ✅ Debugging Log 추가
            logger.info(f"[Before Deduction] Ingredient: {ingredient.name}, Remaining Stock: {inventory.remaining_stock}")
            print(f"[Before Deduction] Ingredient: {ingredient.name}, Remaining Stock: {inventory.remaining_stock}")

            # ✅ 모든 연산에 Decimal 적용
            inventory.remaining_stock = Decimal(str(inventory.remaining_stock))  # ✅ Decimal 변환 추가
            required_amount = Decimal(str(ingredient_data["quantity_used"]))  
            unit_price = Decimal(str(ingredient.unit_cost))  

            logger.info(f"[Check] Ingredient: {ingredient.name}, Unit Cost: {unit_price}, Required Amount: {required_amount}")
            print(f"[Check] Ingredient: {ingredient.name}, Unit Cost: {unit_price}, Required Amount: {required_amount}")

            if inventory.remaining_stock < required_amount:
                raise serializers.ValidationError(
                    f"{ingredient.name} 재고가 부족합니다. (남은 재고: {inventory.remaining_stock})"
                )

            inventory.remaining_stock -= required_amount  
            inventory.save()

            logger.info(f"[After Deduction] Ingredient: {ingredient.name}, Remaining Stock: {inventory.remaining_stock}")
            print(f"[After Deduction] Ingredient: {ingredient.name}, Remaining Stock: {inventory.remaining_stock}")

            RecipeItem.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity_used=required_amount,
                unit=ingredient_data["unit"]
            )

            # ✅ `ingredient_costs`에 추가 (모든 값 Decimal 변환)
            ingredient_costs.append({
                "ingredient_id": str(ingredient.id),
                "ingredient_name": ingredient.name,
                "unit_price": unit_price,  
                "quantity_used": required_amount,
                "unit": ingredient_data["unit"]
            })

        cost_data = calculate_recipe_cost(
            ingredients=ingredient_costs,
            sales_price_per_item=Decimal(str(recipe.sales_price_per_item)),  
            production_quantity_per_batch=Decimal(str(recipe.production_quantity_per_batch))  
        )

        # ✅ Debugging Log for Cost Calculation
        logger.info(f"Calculated Cost Data: {cost_data}")
        print(f"Calculated Cost Data: {cost_data}")

        recipe.total_ingredient_cost = cost_data["total_material_cost"]
        recipe.production_cost = cost_data["cost_per_item"]

        return recipe


    def get_total_ingredient_cost(self, obj):
        """✅ 응답에 `total_ingredient_cost` 추가 (None 방지)"""
        return getattr(obj, "total_ingredient_cost", 0)

    def get_production_cost(self, obj):
        """✅ 응답에 `production_cost` 추가 (None 방지)"""
        return getattr(obj, "production_cost", 0)
