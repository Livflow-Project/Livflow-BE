from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction  # ✅ 트랜잭션 적용
from .models import Inventory
from ingredients.models import Ingredient
from costcalcul.models import Recipe, RecipeItem  # ✅ 레시피 모델 추가
from .serializers import InventorySerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests


# ✅ 특정 상점의 재고 조회
class StoreInventoryView(APIView):
    
    @swagger_auto_schema(
        operation_summary="특정 상점의 재고 목록 조회",
        responses={200: "재고 목록 반환"}
    )
    
    def get(self, request, store_id):
        """ 특정 상점의 재고 목록 조회 """
        inventories = Inventory.objects.filter(ingredient__store_id=store_id)
        inventory_data = [
            {
                "ingredient_id": str(inv.ingredient.id),
                "ingredient_name": inv.ingredient.name,
                "original_stock": inv.ingredient.purchase_quantity,
                "remaining_stock": inv.remaining_stock,
                "unit": inv.ingredient.unit,
                "unit_cost": inv.ingredient.unit_cost,  # ✅ unit_cost 추가
            }
            for inv in inventories
        ]
        return Response(inventory_data, status=status.HTTP_200_OK)

 
class UseIngredientStockView(APIView):

    @swagger_auto_schema(
        operation_summary="특정 재료 재고 사용",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "used_stock": openapi.Schema(type=openapi.TYPE_NUMBER, description="사용할 재고량")
            },
            required=["used_stock"]
        ),
        responses={200: "재고 사용 성공", 400: "유효성 검사 실패"}
    )
    
    
    def post(self, request, store_id, ingredient_id):
        inventory = get_object_or_404(Inventory, ingredient__id=ingredient_id, ingredient__store_id=store_id)
        used_stock = request.data.get("used_stock")

        print(f"🔍 [요청 수신] ingredient_id: {ingredient_id}, 사용 요청: {used_stock}, 현재 재고: {inventory.remaining_stock}")

        if used_stock is None or not isinstance(used_stock, (int, float)) or used_stock <= 0:
            return Response({"error": "유효한 사용량(used_stock)을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        if inventory.remaining_stock < used_stock:
            return Response({"error": "남은 재고보다 많이 사용할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        print(f"✅ 재고 차감 전: {inventory.remaining_stock}, 차감할 수량: {used_stock}")

        # 🚀 여기에서 재고 차감이 두 번 발생하는지 확인
        inventory.remaining_stock -= used_stock
        print(f"✅ 재고 차감 후: {inventory.remaining_stock}")  

        inventory.save()
        
        return Response({
            "ingredient_id": inventory.ingredient.id,
            "ingredient_name": inventory.ingredient.name,
            "remaining_stock": inventory.remaining_stock,
            "unit": inventory.ingredient.unit,
        }, status=status.HTTP_200_OK)



# ✅ 레시피 삭제 시 재료 재고 복구
class DeleteRecipeView(APIView):
    
    @swagger_auto_schema(
        operation_summary="레시피 삭제 및 재료 재고 복구",
        responses={204: "레시피 삭제 및 재고 복구 완료", 404: "레시피를 찾을 수 없음"}
    )    
    def delete(self, request, store_id, recipe_id):
        """ 레시피 삭제 시 사용한 재료를 다시 재고로 복구 """
        recipe = get_object_or_404(Recipe, id=recipe_id, store_id=store_id)
        recipe_items = RecipeItem.objects.filter(recipe=recipe)

        with transaction.atomic():  # ✅ 트랜잭션 적용
            for item in recipe_items:
                inventory_item = Inventory.objects.filter(ingredient=item.ingredient).first()
                if inventory_item:
                    max_stock = inventory_item.ingredient.purchase_quantity  # ✅ original_stock 대체
                    inventory_item.remaining_stock = min(
                        inventory_item.remaining_stock + item.quantity_used,
                        max_stock  # ✅ original_stock 초과 방지
                    )
                    inventory_item.save()

            # ✅ 레시피 및 연결된 RecipeItem 삭제
            recipe_items.delete()
            recipe.delete()

        return Response({"message": "레시피 삭제 및 재고 복구 완료"}, status=status.HTTP_204_NO_CONTENT)


