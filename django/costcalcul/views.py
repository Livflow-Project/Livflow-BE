from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe, RecipeItem
from .serializers import RecipeSerializer
from django.shortcuts import get_object_or_404
from ingredients.models import Ingredient  # ✅ Ingredient 모델 import
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from inventory.models import Inventory
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema

# ✅ 특정 상점의 모든 레시피 조회
class StoreRecipeListView(APIView):
    parser_classes = (JSONParser,MultiPartParser, FormParser)
    
    @swagger_auto_schema(
        operation_summary="특정 상점의 모든 레시피 조회",
        responses={200: "레시피 목록 반환"}
    )
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

    @swagger_auto_schema(
        operation_summary="새로운 레시피 추가",
        request_body=RecipeSerializer,
        responses={201: "레시피 생성 성공", 400: "유효성 검사 실패"}
    )

    def post(self, request, store_id):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                recipe = serializer.save(store_id=store_id)  # ✅ 원가 계산은 `serializer.create()`에서 실행됨

                print(f"🔍 Step 1 - Recipe Created: {recipe.id}")

                # ✅ 응답 데이터 생성 (DB에서 가져온 최신 값 사용)
                updated_recipe = Recipe.objects.get(id=recipe.id)

                response_data = {
                    "id": str(updated_recipe.id),
                    "recipe_name": updated_recipe.name,
                    "recipe_cost": updated_recipe.sales_price_per_item,
                    "recipe_img": updated_recipe.recipe_img.url if updated_recipe.recipe_img else None,
                    "is_favorites": updated_recipe.is_favorites,
                    "production_quantity": updated_recipe.production_quantity_per_batch,
                    "total_ingredient_cost": float(updated_recipe.total_ingredient_cost),  # ✅ 최신 DB 값 사용
                    "production_cost": float(updated_recipe.production_cost),  # ✅ 최신 DB 값 사용
                }

                print(f"📌 Final API Response: {response_data}")

                return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ 특정 레시피 상세 조회
class StoreRecipeDetailView(APIView):
    parser_classes = (JSONParser,MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="특정 레시피 상세 조회",
        responses={200: "레시피 상세 정보 반환", 404: "레시피를 찾을 수 없음"}
    )

    def get(self, request, store_id, recipe_id):
        """ 특정 레시피 상세 조회 """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        ingredients = RecipeItem.objects.filter(recipe=recipe)

        # ✅ 각 재료의 정보 가져오기
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

        # ✅ DB에서 저장된 원가 값 가져오기
        response_data = {
            "recipe_id": str(recipe.id),  
            "recipe_name": recipe.name,
            "recipe_cost": recipe.sales_price_per_item,
            "recipe_img": recipe.recipe_img.url if recipe.recipe_img else None,
            "is_favorites": recipe.is_favorites,
            "ingredients": ingredients_data,  # ✅ 재료 정보 추가
            "total_ingredient_cost": float(recipe.total_ingredient_cost),  # ✅ DB 값 가져오기
            "production_quantity": recipe.production_quantity_per_batch,
            "production_cost": float(recipe.production_cost),  # ✅ DB 값 가져오기
        }

        print(f"📌 Final API Response: {response_data}")  # ✅ 최종 응답 확인

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="특정 레시피 수정",
        request_body=RecipeSerializer,
        responses={200: "레시피 수정 성공", 400: "유효성 검사 실패", 404: "레시피를 찾을 수 없음"}
    )

    def put(self, request, store_id, recipe_id):
        """ 특정 레시피 수정 """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)

        if serializer.is_valid():
            recipe = serializer.save()

            # ✅ ingredients가 있으면 업데이트, 없으면 기존 값 유지
            ingredients = request.data.get("ingredients", None)
            if ingredients is not None:  
                RecipeItem.objects.filter(recipe=recipe).delete()
                for ingredient_data in ingredients:
                    ingredient = get_object_or_404(Ingredient, id=ingredient_data["ingredient_id"])
                    RecipeItem.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity_used=ingredient_data["required_amount"],
                    )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="특정 레시피 삭제",
        responses={204: "레시피 삭제 성공", 404: "레시피를 찾을 수 없음"}
    )

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

