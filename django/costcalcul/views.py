from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe, RecipeItem
from .serializers import RecipeSerializer
from django.shortcuts import get_object_or_404
from ingredients.models import Ingredient  
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from inventory.models import Inventory
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from decimal import Decimal
import json
from .utils import get_total_used_quantity
from copy import deepcopy

# ✅ 특정 상점의 모든 레시피 조회
class StoreRecipeListView(APIView):
    parser_classes = (JSONParser,MultiPartParser, FormParser)
    
    @swagger_auto_schema(
        operation_summary="특정 상점의 모든 레시피 조회",
        responses={200: "레시피 목록 반환"}
    )
    def get(self, request, store_id):
        recipes = Recipe.objects.filter(store_id=store_id).order_by("created_at")
        recipe_data = [
            {
                "recipe_id": str(recipe.id),  # ✅ UUID 문자열 변환
                "recipe_name": recipe.name,
                "recipe_cost": recipe.sales_price_per_item if recipe.sales_price_per_item else None,
                "recipe_img": recipe.recipe_img.url if recipe.recipe_img and hasattr(recipe.recipe_img, 'url') else None, 
                "is_favorites": recipe.is_favorites,  
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
        """✅ 새로운 레시피 추가"""

        # ✅ deepcopy 후 dict로 강제 변환 (QueryDict → dict)
        request_data = dict(deepcopy(request.data))

        ingredients = request_data.get("ingredients", None)
        print("🧪 [디버깅] ingredients 타입:", type(ingredients))
        print("🧪 [디버깅] ingredients 내용:", ingredients)

        # ✅ None인 경우 빈 리스트
        if ingredients is None:
            ingredients = []

        # ✅ 문자열이면 JSON 파싱
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                return Response({"error": "올바른 JSON 형식의 ingredients를 보내야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ dict면 리스트로 감싸기
        if isinstance(ingredients, dict):
            ingredients = [ingredients]

        # ✅ 이중 리스트 풀기
        if isinstance(ingredients, list) and len(ingredients) == 1 and isinstance(ingredients[0], list):
            ingredients = ingredients[0]

        # 🔄 최종 반영
        request_data["ingredients"] = ingredients
        print("🧪 [디버깅] 최종 serializer로 넘길 request_data:", request_data)

        serializer = RecipeSerializer(data=request_data)
        if serializer.is_valid():
            with transaction.atomic():
                recipe = serializer.save(
                    store_id=store_id,
                    is_favorites=str(request.data.get("is_favorites", "false")).lower() == "true"
                )

                recipe_img_url = recipe.recipe_img.url if recipe.recipe_img and recipe.recipe_img.name else None

                response_data = {
                    "id": str(recipe.id),
                    "recipe_name": recipe.name,
                    "recipe_cost": recipe.sales_price_per_item,
                    "recipe_img": recipe_img_url,
                    "is_favorites": recipe.is_favorites,
                    "production_quantity": recipe.production_quantity_per_batch,
                    "total_ingredient_cost": float(recipe.total_ingredient_cost),
                    "production_cost": float(recipe.production_cost),
                    "ingredients": ingredients,
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# 특정 레시피 상세 조회
class StoreRecipeDetailView(APIView):
    parser_classes = (JSONParser,MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="특정 레시피 상세 조회",
        responses={200: "레시피 상세 정보 반환", 404: "레시피를 찾을 수 없음"}
    )

    def get(self, request, store_id, recipe_id):
        print("🚀 [레시피 GET] 요청 들어옴:", store_id, recipe_id)
        """ 특정 레시피 상세 조회 """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        ingredients = RecipeItem.objects.filter(recipe=recipe)
        print(f"📦 연결된 재료 개수: {ingredients.count()}")

        ingredients_data = []
        for item in ingredients:
            ingredient = item.ingredient
            required_amount = item.quantity_used

            # ✅ 여기에 있어야 함!
            print(f"🧾 재료: {ingredient.name}, 저장된 사용량: {required_amount}")
            print(f"🔍 구매량: {ingredient.purchase_quantity}, 기존 구매량: {ingredient.original_stock_before_edit}")

            inventory = Inventory.objects.filter(ingredient=ingredient).first()
            if inventory:
                original_stock = Decimal(str(ingredient.purchase_quantity))
                remaining_stock = Decimal(str(inventory.remaining_stock))
                used_stock = original_stock - remaining_stock

                print(f"📉 used_stock: {used_stock}")
                
                #used_stock 프론트값 일치시키기
                #required_amount = used_stock
                
                if ingredient.purchase_quantity < ingredient.original_stock_before_edit:
                    print("🌀 구매량 감소 감지 → required_amount = 0 처리")
                    required_amount = Decimal("0.0")

            ingredients_data.append({
                "ingredient_id": str(ingredient.id),
                "required_amount": float(required_amount)
            })



        # 이미지 예외 처리
        recipe_img_url = None
        if recipe.recipe_img and hasattr(recipe.recipe_img, 'url'):
            recipe_img_url = recipe.recipe_img.url

        response_data = {
            "recipe_id": str(recipe.id),
            "recipe_name": recipe.name,
            "recipe_cost": recipe.sales_price_per_item,
            "recipe_img": recipe_img_url,
            "is_favorites": recipe.is_favorites,
            "ingredients": ingredients_data,
            "production_quantity": recipe.production_quantity_per_batch,
        }

        return Response(response_data, status=status.HTTP_200_OK)




    @swagger_auto_schema(
        operation_summary="특정 레시피 수정",
        request_body=RecipeSerializer,
        responses={200: "레시피 수정 성공", 400: "유효성 검사 실패", 404: "레시피를 찾을 수 없음"}
    )


    def put(self, request, store_id, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        request_data = request.data.copy()
        partial = True

        # ✅ 이미지 디버깅
        print(f"📂 request.FILES: {request.FILES}")
        image_file = request.FILES.get('recipe_img')
        print(f"📸 image_file: {image_file}")

        # ✅ 이미지 필드 강제 삽입
        if image_file:
            request_data['recipe_img'] = image_file
            print("✅ 이미지가 request_data에 추가됨.")
        elif "recipe_img" not in request_data:
            request_data["recipe_img"] = recipe.recipe_img if recipe.recipe_img and recipe.recipe_img.name else None
            print("📎 기존 이미지 유지")
        elif request_data.get("recipe_img") in [None, "null", "", "None"]:
            if recipe.recipe_img and recipe.recipe_img.name:
                img_name = recipe.recipe_img.name
                recipe.recipe_img.delete(save=False)
                print(f"🧹 이미지 삭제 완료: {img_name}")
            request_data["recipe_img"] = None
            print("❌ 이미지 삭제 요청 처리됨.")

        print(f"📦 request_data['recipe_img']: {request_data.get('recipe_img')}")

        # ✅ ingredients 처리
        ingredients = request_data.get("ingredients", [])
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                return Response({"error": "올바른 JSON 형식의 ingredients를 보내야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        updated_ingredients = []

        for ing in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ing.get("ingredient_id"))
            inventory = Inventory.objects.filter(ingredient=ingredient).first()

            required_amount = Decimal(str(ing.get("required_amount", 0)))

            if inventory:
                current_capacity = Decimal(str(ingredient.purchase_quantity))
                remaining_stock = Decimal(str(inventory.remaining_stock))
                total_used = get_total_used_quantity(ingredient)

                estimated_old_capacity = current_capacity + total_used

                print(f"\n🧾 [디버깅] Ingredient: {ingredient.name}")
                print(f"📦 이전 구매량 추정: {estimated_old_capacity}, 현재 구매량: {current_capacity}")
                print(f"📏 기존 required_amount: {required_amount}, 총 사용량: {total_used}")

                # ✅ 백업이 안 되어 있다면 현재 값을 백업
                if ingredient.original_stock_before_edit == 0 and ingredient.purchase_quantity > 0:
                    print(f"📝 original_stock_before_edit 백업: {ingredient.purchase_quantity}")
                    ingredient.original_stock_before_edit = ingredient.purchase_quantity
                    ingredient.save()

                # ✅ 초기화 조건
                if current_capacity < estimated_old_capacity and required_amount != 0 and total_used == 0:
                    print("⚠️ 조건 충족 → required_amount 초기화")
                    required_amount = Decimal("0.0")

            ing["required_amount"] = float(required_amount)
            updated_ingredients.append(ing)


        request_data["ingredients"] = updated_ingredients

        # ✅ serializer에 FILES도 함께 넘김
        serializer = RecipeSerializer(instance=recipe, data=request_data, partial=partial)

        if not serializer.is_valid():
            print(f"🚨 serializer.errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        recipe = serializer.save()
        
        with transaction.atomic():
            recipe.is_favorites = str(request.data.get("is_favorites", str(recipe.is_favorites).lower())).lower() == "true"
            recipe.save()

            RecipeItem.objects.filter(recipe=recipe).delete()

            for ingredient_data in updated_ingredients:
                ingredient = get_object_or_404(Ingredient, id=ingredient_data.get("ingredient_id"))
                required_amount = Decimal(str(ingredient_data.get("required_amount", 0)))

                RecipeItem.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity_used=required_amount,
                )

        print(f"✅ 최종 저장된 이미지: {recipe.recipe_img}")
        print(f"✅ 최종 저장된 이미지 URL: {recipe.recipe_img.url if recipe.recipe_img else 'None'}")

        return Response(RecipeSerializer(recipe).data, status=status.HTTP_200_OK)





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