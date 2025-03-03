from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe, RecipeItem
from .serializers import RecipeSerializer
from django.shortcuts import get_object_or_404
import uuid

# 특정 상점의 모든 레시피 조회
class StoreRecipeListView(APIView):
    def get(self, request, store_id):
        recipes = Recipe.objects.filter(store_id=store_id)
        recipe_data = [
            {
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "recipe_cost": recipe.sales_price_per_item if recipe.sales_price_per_item else None,
                "recipe_img": recipe.recipe_img if recipe.recipe_img else None,
                "is_favorites": False,  # 기본값 설정
            }
            for recipe in recipes
        ]
        return Response(recipe_data, status=status.HTTP_200_OK)

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



# 특정 레시피 상세 조회
class StoreRecipeDetailView(APIView):
    def get(self, request, store_id, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        ingredients = RecipeItem.objects.filter(recipe=recipe)

        ingredients_data = [
            {
                "ingredient_id": str(uuid.uuid4()),  # UUID 생성
                "ingredient_name": item.ingredient.name,
                "required_amount": item.quantity_used,
                "unit": item.unit
            }
            for item in ingredients
        ]

        response_data = {
            "recipe_id": str(uuid.uuid4()),  # UUID 생성
            "recipe_name": recipe.name,
            "recipe_cost": recipe.sales_price_per_item if recipe.sales_price_per_item else None,
            "recipe_img": recipe.recipe_img if recipe.recipe_img else None,
            "is_favorites": False,  # 기본값 설정
            "ingredients": ingredients_data,
            "total_ingredient_cost": recipe.total_material_cost,
            "production_quantity": recipe.production_quantity_per_batch,
            "production_cost": recipe.material_cost_per_item,
        }

        return Response(response_data, status=status.HTTP_200_OK)



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


