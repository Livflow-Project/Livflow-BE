from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe, RecipeItem, Ingredient
from .serializers import RecipeSerializer
from django.shortcuts import get_object_or_404
import uuid

# 특정 상점의 모든 레시피 조회
class StoreRecipeListView(APIView):
    def get(self, request, store_id):
        recipes = Recipe.objects.filter(store_id=store_id)
        recipe_data = []

        for recipe in recipes:
            recipe_info = {
                "recipe_id": recipe.id,
                "recipe_name": recipe.name
            }
            if recipe.sales_price_per_item:
                recipe_info["recipe_cost"] = recipe.sales_price_per_item
            if recipe.recipe_img:
                recipe_info["recipe_img"] = recipe.recipe_img

            recipe_data.append(recipe_info)

        return Response(recipe_data, status=status.HTTP_200_OK)


# 특정 레시피 상세 조회
class StoreRecipeDetailView(APIView):
    def get(self, request, store_id, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        ingredients = RecipeItem.objects.filter(recipe=recipe)

        ingredients_data = [
            {
                "ingredient_id": item.ingredient.id,
                "ingredient_name": item.ingredient.name,
                "required_amount": item.quantity_used,
                "unit": item.unit
            }
            for item in ingredients
        ]

        response_data = {
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "ingredients": ingredients_data
        }
        if recipe.sales_price_per_item:
            response_data["recipe_cost"] = recipe.sales_price_per_item
        if recipe.recipe_img:
            response_data["recipe_img"] = recipe.recipe_img
        if recipe.production_quantity_per_batch:
            response_data["production_quantity"] = recipe.production_quantity_per_batch

        # 총 원가 및 생산 단가 계산
        total_ingredient_cost = sum(item.ingredient.unit_cost * item.quantity_used for item in ingredients)
        response_data["total_ingredient_cost"] = total_ingredient_cost
        if recipe.production_quantity_per_batch:
            response_data["production_cost"] = total_ingredient_cost / recipe.production_quantity_per_batch

        return Response(response_data, status=status.HTTP_200_OK)


# 새로운 레시피 생성
class StoreRecipeCreateView(APIView):
    def post(self, request, store_id):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            recipe = serializer.save(store_id=store_id)

            # 요청된 재료 처리
            ingredients = request.data.get("ingredients", [])
            for ingredient_data in ingredients:
                ingredient = get_object_or_404(Ingredient, id=ingredient_data["ingredient_id"])
                RecipeItem.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity_used=ingredient_data["required_amount"],
                    unit=ingredient_data["unit"]
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 특정 레시피 수정
class StoreRecipeUpdateView(APIView):
    def put(self, request, store_id, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)

        if serializer.is_valid():
            recipe = serializer.save()

            # 기존 재료 삭제 후 새로운 재료 추가
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


# 특정 레시피 삭제
class StoreRecipeDeleteView(APIView):
    def delete(self, request, store_id, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        recipe.delete()
        return Response({"message": "레시피가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

# 특정 상점의 모든 재료 및 남은 재고 조회
class StoreInventoryView(APIView):
    def get(self, request, store_id):
        ingredients = Ingredient.objects.filter(store_id=store_id)
        inventory_data = [
            {
                "ingredient_id": str(uuid.uuid4()),  # UUID 생성 (프론트엔드 요구사항 반영)
                "ingredient_name": ingredient.name,
                "remaining_stock": ingredient.purchase_quantity,  # 초기값은 purchase_quantity
                "unit": ingredient.unit,
            }
            for ingredient in ingredients
        ]
        return Response(inventory_data, status=status.HTTP_200_OK)


# 특정 재료 등록 후 초기 재고 설정
class IngredientCreateView(APIView):
    def post(self, request, store_id):
        data = request.data
        ingredient = Ingredient.objects.create(
            store_id=store_id,
            name=data.get("name"),
            purchase_price=data.get("purchase_price"),
            purchase_quantity=data.get("purchase_quantity"),  # 초기값 설정
            unit=data.get("unit"),
            vendor=data.get("vendor", ""),
            notes=data.get("notes", "")
        )

        response_data = {
            "ingredient_id": str(uuid.uuid4()),  # UUID 반환
            "ingredient_name": ingredient.name,
            "remaining_stock": ingredient.purchase_quantity,
            "unit": ingredient.unit,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


# 특정 재료 사용 (재고 감소)
class UseIngredientStockView(APIView):
    def post(self, request, store_id, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        used_stock = request.data.get("used_stock")

        if used_stock is None or used_stock <= 0:
            return Response({"error": "유효한 used_stock 값을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        if ingredient.purchase_quantity < used_stock:
            return Response({"error": "재고가 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)

        ingredient.purchase_quantity -= used_stock  # 남은 재고 감소
        ingredient.save()

        return Response({
            "ingredient_id": ingredient.id,
            "ingredient_name": ingredient.name,
            "remaining_stock": ingredient.purchase_quantity,
            "unit": ingredient.unit,
        }, status=status.HTTP_200_OK)