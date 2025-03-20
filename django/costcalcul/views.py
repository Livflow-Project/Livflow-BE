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
from decimal import Decimal
from django.utils.timezone import now
import json

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
                "recipe_img": recipe.recipe_img.url if recipe.recipe_img and hasattr(recipe.recipe_img, 'url') else None, 
                "is_favorites": recipe.is_favorites,  # ✅ 기본값 설정 (프론트엔드 요구사항 반영)
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
        """✅ 새로운 레시피 추가 (FormData & JSON 처리)"""
        print(f"🔍 [레시피 저장 요청] store_id: {store_id}, 데이터: {request.data}")

        request_data = request.data.copy()

        # ✅ `ingredients`가 문자열이면 JSON 변환
        ingredients = request_data.get("ingredients", [])
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                return Response({"error": "올바른 JSON 형식의 ingredients를 보내야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        request_data["ingredients"] = ingredients

        serializer = RecipeSerializer(data=request_data)
        if serializer.is_valid():
            with transaction.atomic():
                recipe = serializer.save(
                    store_id=store_id,
                    is_favorites=str(request.data.get("is_favorites", "false")).lower() == "true"
                )

                print(f"🔍 Step 1 - Recipe Created: {recipe.id}")

                # ✅ 이미지 없을 경우 예외 처리 추가
                recipe_img_url = None
                if recipe.recipe_img and hasattr(recipe.recipe_img, 'url'):
                    recipe_img_url = recipe.recipe_img.url

                # ✅ 빈 배열일 경우 자동으로 처리
                response_data = {
                    "id": str(recipe.id),
                    "recipe_name": recipe.name,
                    "recipe_cost": recipe.sales_price_per_item,
                    "recipe_img": recipe.recipe_img.url if recipe.recipe_img else None,
                    "is_favorites": recipe.is_favorites,
                    "production_quantity": recipe.production_quantity_per_batch,
                    "total_ingredient_cost": float(recipe.total_ingredient_cost),
                    "production_cost": float(recipe.production_cost),
                    "ingredients": ingredients,  # 자동으로 빈 배열이 들어감
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
                "required_amount": item.quantity_used  # ✅ 필요한 데이터만 포함
            }
            for item in ingredients
    ]
        
        # ✅ 이미지 예외 처리 추가
        recipe_img_url = None
        if recipe.recipe_img and hasattr(recipe.recipe_img, 'url'):
            recipe_img_url = recipe.recipe_img.url

        # ✅ 응답 데이터 변환
        response_data = {
            "recipe_id": str(recipe.id),  # ✅ UUID 유지 (프론트에서 crypto.randomUUID()로 변경)
            "recipe_name": recipe.name,
            "recipe_cost": recipe.sales_price_per_item,
            "recipe_img": recipe.recipe_img.url if recipe.recipe_img else None, 
            "is_favorites": recipe.is_favorites,  # ✅ 항상 true로 설정
            "ingredients": ingredients_data,  # ✅ 필요한 필드만 유지
            "production_quantity": recipe.production_quantity_per_batch,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="특정 레시피 수정",
        request_body=RecipeSerializer,
        responses={200: "레시피 수정 성공", 400: "유효성 검사 실패", 404: "레시피를 찾을 수 없음"}
    )

    def put(self, request, store_id, recipe_id):
        """✅ 특정 레시피 수정 (FormData & JSON 처리 + 이미지 유지)"""
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        request_data = request.data.copy()
        partial = True  # 일부 필드만 업데이트 가능하도록 설정

        # ✅ `recipe_img`가 없으면 기존 이미지 유지
        if "recipe_img" not in request_data:
            request_data["recipe_img"] = recipe.recipe_img  # 기존 이미지 유지
            
        # ✅ `recipe_img`가 비어 있으면 기존 이미지 제거
        elif not request_data["recipe_img"]:
            request_data["recipe_img"] = None  # 이미지 삭제
    

        # ✅ `ingredients`가 문자열이면 JSON 변환
        ingredients = request_data.get("ingredients", [])
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                return Response({"error": "올바른 JSON 형식의 ingredients를 보내야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        request_data["ingredients"] = ingredients
        serializer = RecipeSerializer(recipe, data=request_data, partial=partial)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # ✅ is_favorites 값 업데이트
            recipe.is_favorites = str(request.data.get("is_favorites", str(recipe.is_favorites).lower())).lower() == "true"
            recipe.save()

            # ✅ 기존 재료 삭제 (복구 로직 제거)
            RecipeItem.objects.filter(recipe=recipe).delete()

            # ✅ 새로운 재료 반영 (remaining_stock 수정 X)
            if isinstance(ingredients, list):  
                for ingredient_data in ingredients:
                    ingredient = get_object_or_404(Ingredient, id=ingredient_data.get("ingredient_id"))
                    required_amount = Decimal(str(ingredient_data.get("required_amount", 0)))

                    RecipeItem.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity_used=required_amount,
                    )

        # ✅ 최신 레시피 데이터 반환 (업데이트된 ingredients 포함)
        updated_recipe = Recipe.objects.get(id=recipe.id)  
        return Response(RecipeSerializer(updated_recipe).data, status=status.HTTP_200_OK)

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
                    inventory.remaining_stock = Decimal(str(inventory.remaining_stock))  # float → Decimal 변환
                    inventory.remaining_stock += item.quantity_used  # ✅ Decimal + Decimal 연산 가능
                    inventory.save()

            recipe_items.delete()  # ✅ 사용한 RecipeItem 삭제
            recipe.delete()  # ✅ 레시피 삭제

        return Response({"message": "레시피가 삭제되었으며, 사용한 재료의 재고가 복구되었습니다."}, status=status.HTTP_204_NO_CONTENT)

