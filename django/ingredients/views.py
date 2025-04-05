from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Ingredient
from inventory.models import Inventory
from .serializers import IngredientSerializer
from store.models import Store
from drf_yasg.utils import swagger_auto_schema
from decimal import Decimal
from costcalcul.models import RecipeItem

class StoreIngredientView(APIView):
    """
    특정 상점의 모든 재료를 조회하고, 새로운 재료를 추가하는 API
    """

    @swagger_auto_schema(
        operation_summary="특정 상점의 모든 재료 조회",
        responses={200: "재료 목록 반환"}
    )

    def get(self, request, store_id):
        """ 특정 상점의 모든 재료 조회 (Ingredient 기준) """
        ingredients = Ingredient.objects.filter(store_id=store_id).order_by("created_at")
        ingredient_data = [
            {
                "ingredient_id": str(ingredient.id),
                "ingredient_name": ingredient.name,
                "ingredient_cost": ingredient.purchase_price,
                "capacity": ingredient.purchase_quantity,  # 원래 등록된 구매 용량 기준
                "unit": ingredient.unit,
                "unit_cost": ingredient.unit_cost,
                "shop": ingredient.vendor if ingredient.vendor else None,
                "ingredient_detail": ingredient.notes if ingredient.notes else None,
            }
            for ingredient in ingredients
        ]
        return Response(ingredient_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="특정 상점에 새로운 재료 추가",
        request_body=IngredientSerializer,
        responses={201: "재료 추가 성공", 400: "유효성 검사 실패"}
    )

    def post(self, request, store_id):
        """ 특정 상점에 재료 추가 """
        store = get_object_or_404(Store, id=store_id)
        data = request.data.copy()
        data["store"] = store.id  # store_id가 없을 수 있으니 직접 입력

        with transaction.atomic():  # 트랜잭션 적용
            serializer = IngredientSerializer(data=data)# 받아온 데이터를 역직렬화함
            if serializer.is_valid(): # serializer 필수 데이터타입이 맞는지 검증
                ingredient = serializer.save(store=store)  # store_id 저장

                # Inventory 자동 추가(데이터 값을 inventory에 넣기)
                Inventory.objects.create(
                    ingredient=ingredient,
                    remaining_stock=ingredient.purchase_quantity,
                )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientDetailView(APIView):
    """
    특정 재료를 조회, 수정 및 삭제하는 API
    """

    @swagger_auto_schema(
        operation_summary="특정 재료 상세 조회",
        responses={200: "재료 상세 정보 반환", 404: "재료를 찾을 수 없음"}
    )

    def get(self, request, store_id, ingredient_id):
        """ 특정 재료 상세 조회 """
        inventory = get_object_or_404(Inventory, ingredient__id=ingredient_id, ingredient__store_id=store_id)
        ingredient = inventory.ingredient  # Inventory에서 Ingredient 가져오기
        data = {
            "ingredient_id": str(ingredient.id),
            "ingredient_name": ingredient.name,
            "ingredient_cost": ingredient.purchase_price,
            "capacity": ingredient.purchase_quantity, # 구매용량
            "unit": ingredient.unit,
            "unit_cost": ingredient.unit_cost,
            "shop": ingredient.vendor if ingredient.vendor else None,
            "ingredient_detail": ingredient.notes if ingredient.notes else None,
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="특정 재료 수정",
        request_body=IngredientSerializer,
        responses={200: "재료 수정 성공", 400: "유효성 검사 실패", 404: "재료를 찾을 수 없음"}
    )

    def put(self, request, store_id, ingredient_id):
        """ 특정 재료 수정 (original_stock 감소 시 used_stock을 0으로 초기화) """
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)

        if serializer.is_valid():
            old_original_stock = Decimal(str(ingredient.purchase_quantity))  # 기존 original_stock
            new_original_stock = request.data.get("capacity")

            if new_original_stock is not None:
                new_original_stock = Decimal(str(new_original_stock))
            else:
                new_original_stock = old_original_stock  # 값이 없으면 기존 값 유지

            difference = new_original_stock - old_original_stock  # 용량 변화량 계산
            # print(f" 기존 original_stock: {old_original_stock}, 새로운 original_stock: {new_original_stock}, 차이: {difference}")

            inventory = Inventory.objects.filter(ingredient=ingredient).first()

            if inventory:
                # print(f" 기존 remaining_stock: {inventory.remaining_stock}, 변동 차이: {difference}")

                inventory.remaining_stock = Decimal(str(inventory.remaining_stock))

                #  **original_stock 증가 → remaining_stock 증가**
                if difference > 0:
                    inventory.remaining_stock += difference
                    # print(f" 증가 적용 - 새로운 remaining_stock: {inventory.remaining_stock}")

                #  **original_stock 감소 → used_stock을 0으로 설정 & remaining_stock 재조정**
                elif difference < 0:
                    # print(f"⚠️ original_stock 감소 감지! used_stock 초기화 적용")

                    #  백업 로직 추가
                    if ingredient.original_stock_before_edit == 0:
                        ingredient.original_stock_before_edit = old_original_stock
                        # print(f" original_stock_before_edit 백업: {old_original_stock}")
                        ingredient.save()

                    #  used_stock 초기화
                    used_stock = old_original_stock - inventory.remaining_stock
                    # print(f" 기존 사용량(used_stock): {used_stock} → 초기화 (0)")

                    # remaining_stock을 new_original_stock으로 재설정
                    inventory.remaining_stock = new_original_stock
                    # print(f"remaining_stock을 new_original_stock({new_original_stock})으로 변경")


                inventory.save()

            #  `original_stock` 반영 후 재료 업데이트
            serializer.save(purchase_quantity=new_original_stock)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="특정 재료 삭제",
        responses={204: "재료 삭제 성공", 404: "재료를 찾을 수 없음"}
    )

    def delete(self, request, store_id, ingredient_id):
        """ 특정 재료 삭제 """
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        ingredient.delete()
        return Response({"message": "재료가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
    
class IngredientUsagesView(APIView):
    """
    특정 재료를 사용하는 레시피(메뉴) 목록 조회 API
    """

    def get(self, request, store_id, ingredient_id):
        """특정 재료를 사용 중인 레시피 리스트 반환"""
        # 해당 재료를 사용하는 RecipeItem 조회
        recipe_items = RecipeItem.objects.filter(ingredient_id=ingredient_id, recipe__store_id=store_id)

        # 레시피 이름 목록 반환
        recipe_names = [item.recipe.name for item in recipe_items]

        return Response(recipe_names, status=status.HTTP_200_OK)