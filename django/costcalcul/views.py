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
        print(f"🔍 [레시피 저장 요청] store_id: {store_id}, 데이터: {request.data}")
        """ 새로운 레시피 추가 (is_favorites 값을 요청받아 저장) """
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                recipe = serializer.save(
                    store_id=store_id,
                    is_favorites=str(request.data.get("is_favorites", "false")).lower() == "true"
                )
                print(f"🔍 Step 1 - Recipe Created: {recipe.id}")

                updated_recipe = Recipe.objects.get(id=recipe.id)

                # ✅ ingredients 처리
                ingredients = request.data.get("ingredients", [])
                if not ingredients:  # 빈 배열이면 메시지 추가
                    ingredients = [{"message": "등록된 재료가 없습니다."}]

                response_data = {
                    "id": str(updated_recipe.id),
                    "recipe_name": updated_recipe.name,
                    "recipe_cost": updated_recipe.sales_price_per_item,
                    "recipe_img": updated_recipe.recipe_img.url if updated_recipe.recipe_img else None,
                    "is_favorites": updated_recipe.is_favorites,
                    "production_quantity": updated_recipe.production_quantity_per_batch,
                    "total_ingredient_cost": float(updated_recipe.total_ingredient_cost),
                    "production_cost": float(updated_recipe.production_cost),
                    "ingredients": ingredients,  # ✅ 빈 배열일 경우 메시지 포함
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
        """ 특정 레시피 수정 (is_favorites 값을 요청받아 저장) """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        print(f"\n🔍 [{now()}] [레시피 수정 요청] recipe_id: {recipe_id}, store_id: {store_id}")

        with transaction.atomic():
            # ✅ is_favorites 값 업데이트
            recipe.is_favorites = str(request.data.get("is_favorites", str(recipe.is_favorites).lower())).lower() == "true"
            recipe.save()

            # ✅ 기존 재료 사용량을 복구
            old_recipe_items = RecipeItem.objects.filter(recipe=recipe)
            for item in old_recipe_items:
                inventory = Inventory.objects.filter(ingredient=item.ingredient).first()
                if inventory:
                    before_restore = inventory.remaining_stock
                    inventory.remaining_stock = Decimal(str(inventory.remaining_stock))  # 🔥 float → Decimal 변환
                    inventory.remaining_stock += item.quantity_used  # ✅ Decimal 연산
                    inventory.save()
                    print(f"✅ [{now()}] [재고 복구] ingredient_id: {item.ingredient.id}, 기존 재고: {before_restore}, 복구된 재고: {inventory.remaining_stock} (+{item.quantity_used})")
            old_recipe_items.delete()

            # ✅ 새로운 재료 반영 (remaining_stock 수정 제거)
            ingredients = request.data.get("ingredients", [])
            if isinstance(ingredients, list):  
                for ingredient_data in ingredients:
                    ingredient = get_object_or_404(Ingredient, id=ingredient_data.get("ingredient_id"))
                    required_amount = Decimal(str(ingredient_data.get("required_amount", 0)))

                    RecipeItem.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity_used=required_amount,
                    )

        print(f"🎉 [{now()}] PUT 요청 완료\n")
        return Response(serializer.data, status=status.HTTP_200_OK)




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

