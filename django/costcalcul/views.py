from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe, RecipeItem
from .serializers import RecipeSerializer
from django.shortcuts import get_object_or_404
from .utils import calculate_recipe_cost  # ✅ 레시피 원가 계산 함수 활용
from ingredients.models import Ingredient  # ✅ Ingredient 모델 import
from rest_framework.parsers import MultiPartParser, FormParser
from inventory.models import Inventory
from django.db import transaction

# ✅ 특정 상점의 모든 레시피 조회
class StoreRecipeListView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request, store_id):
        recipes = Recipe.objects.filter(store_id=store_id)
        recipe_data = [
            {
                "recipe_id": str(recipe.id),  # ✅ UUID 문자열 변환
                "recipe_name": recipe.name,
                "recipe_cost": recipe.sales_price_per_item if recipe.sales_price_per_item else None,
                "recipe_img": recipe.recipe_img if recipe.recipe_img else None,
                "is_favorites": False,  # ✅ 기본값 설정 (프론트엔드 요구사항 반영)
            }
            for recipe in recipes
        ]
        return Response(recipe_data, status=status.HTTP_200_OK)

    def post(self, request, store_id):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():  # ✅ 트랜잭션 적용 (모든 데이터가 정상적으로 처리되도록)
                recipe = serializer.save(store_id=store_id)

                ingredients = request.data.get("ingredients", [])
                inventory_updates = []  # ✅ 롤백을 위한 재고 변경 내역 저장
                
                try:
                    for ingredient_data in ingredients:
                        ingredient = get_object_or_404(Ingredient, id=ingredient_data["ingredient_id"])
                        inventory = get_object_or_404(Inventory, ingredient=ingredient)

                        if inventory.remaining_stock < ingredient_data["required_amount"]:
                            raise ValueError(f"{ingredient.name} 재고가 부족합니다.")  # ✅ 예외 발생 -> 롤백됨

                        inventory.remaining_stock -= ingredient_data["required_amount"]
                        inventory_updates.append((inventory, ingredient_data["required_amount"]))  # ✅ 롤백 대비 저장
                        inventory.save()

                        RecipeItem.objects.create(
                            recipe=recipe,
                            ingredient=ingredient,
                            quantity_used=ingredient_data["required_amount"],
                            unit=ingredient_data["unit"]
                        )

                except ValueError as e:
                    transaction.set_rollback(True)  # ✅ 롤백 처리
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 특정 레시피 상세 조회
class StoreRecipeDetailView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, store_id, recipe_id):
        """ 특정 레시피 상세 조회 """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        ingredients = RecipeItem.objects.filter(recipe=recipe)

        # ✅ 각 재료의 단가 포함한 데이터 구성
        ingredients_data = [
            {
                "ingredient_id": str(item.ingredient.id),  
                "ingredient_name": item.ingredient.name,
                "unit_price": item.ingredient.unit_cost,  
                "required_amount": item.quantity_used, 
                "unit": item.unit
            }
            for item in ingredients
        ]

        # ✅ 레시피 원가 계산 함수 활용
        cost_data = calculate_recipe_cost(
            ingredients=ingredients_data,
            sales_price_per_item=recipe.sales_price_per_item,
            production_quantity_per_batch=recipe.production_quantity_per_batch
        )

        response_data = {
            "recipe_id": str(recipe.id),  
            "recipe_name": recipe.name,
            "recipe_cost": recipe.sales_price_per_item,
            "recipe_img": recipe.recipe_img.url if recipe.recipe_img else None,
            "is_favorites": False,
            "ingredients": cost_data["ingredient_costs"],
            "total_ingredient_cost": cost_data["total_material_cost"],
            "production_quantity": recipe.production_quantity_per_batch,
            "production_cost": cost_data["cost_per_item"],
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, store_id, recipe_id):
        """ 특정 레시피 수정 """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)

        if serializer.is_valid():
            recipe = serializer.save()

            # ✅ 기존 재료 삭제 후 새로운 재료 추가
            RecipeItem.objects.filter(recipe=recipe).delete()
            ingredients = request.data.get("ingredients", [])
            for ingredient_data in ingredients:
                ingredient = get_object_or_404(Ingredient, id=ingredient_data["ingredient_id"])
                RecipeItem.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity_used=ingredient_data["required_amount"],
                    unit=ingredient_data["unit"]
                )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, store_id, recipe_id):
        """ 특정 레시피 삭제 시 사용한 재료의 재고 복구 """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)

        with transaction.atomic():  # ✅ 트랜잭션 적용
            recipe_items = RecipeItem.objects.filter(recipe=recipe)

            for item in recipe_items:
                inventory = Inventory.objects.filter(ingredient=item.ingredient).first()  # ✅ 존재 여부 체크
                if inventory:
                    inventory.remaining_stock += item.quantity_used  # ✅ 사용량 복구
                    inventory.save()

            recipe_items.delete()  # ✅ 사용한 RecipeItem 삭제
            recipe.delete()  # ✅ 레시피 삭제

        return Response({"message": "레시피가 삭제되었으며, 사용한 재료의 재고가 복구되었습니다."}, status=status.HTTP_204_NO_CONTENT)

