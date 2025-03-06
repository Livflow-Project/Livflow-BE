from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ingredient
from inventory.models import Inventory  # ✅ Inventory 모델 사용
from .serializers import IngredientSerializer
from inventory.serializers import InventorySerializer

class StoreInventoryView(APIView):
    def get(self, request, store_id):
        """특정 상점의 모든 재료 조회 (Inventory 기준)"""
        inventories = Inventory.objects.filter(ingredient__store_id=store_id)  # ✅ Inventory 모델에서 조회

        inventory_data = [
            {
                "ingredient_id": str(inv.ingredient.id),  # ✅ UUID 변환
                "ingredient_name": inv.ingredient.name,
                "ingredient_cost": inv.ingredient.purchase_price,  # ✅ 재료 가격
                "capacity": inv.remaining_stock,  # ✅ 남은 재고 용량
                "unit": inv.ingredient.unit,  
                "unit_cost": inv.ingredient.unit_cost,  # ✅ 자동 계산된 단가
                "shop": inv.ingredient.vendor if inv.ingredient.vendor else None,  # ✅ 선택값
                "ingredient_detail": inv.ingredient.notes if inv.ingredient.notes else None,  # ✅ 선택값
            }
            for inv in inventories
        ]
        return Response(inventory_data, status=status.HTTP_200_OK)

    def post(self, request, store_id):
        """특정 상점에 재료 추가"""
        data = request.data.copy()
        data["store"] = store_id
        serializer = IngredientSerializer(data=data)

        if serializer.is_valid():
            ingredient = serializer.save()  # ✅ Ingredient 저장

            # ✅ Inventory 자동 추가
            inventory_data = {
                "ingredient": ingredient.id,
                "remaining_stock": ingredient.purchase_quantity,
            }
            inventory_serializer = InventorySerializer(data=inventory_data)
            if inventory_serializer.is_valid():
                inventory_serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 특정 재료 상세 조회, 수정, 삭제 (하나의 View에서 처리)
class IngredientDetailView(APIView):
    def get(self, request, store_id, ingredient_id):
        """특정 재료 상세 조회"""
        inventory = get_object_or_404(Inventory, ingredient__id=ingredient_id, ingredient__store_id=store_id)
        ingredient = inventory.ingredient  # ✅ Inventory에서 Ingredient 가져오기
        data = {
            "ingredient_id": str(ingredient.id),
            "ingredient_name": ingredient.name,
            "ingredient_cost": ingredient.purchase_price,
            "capacity": inventory.remaining_stock,  # ✅ 현재 남은 재고
            "unit": ingredient.unit,
            "unit_cost": ingredient.unit_cost,
            "shop": ingredient.vendor if ingredient.vendor else None,
            "ingredient_detail": ingredient.notes if ingredient.notes else None,
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, store_id, ingredient_id):
        """특정 재료 수정"""
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, store_id, ingredient_id):
        """특정 재료 삭제"""
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        ingredient.delete()
        return Response({"message": "재료가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

