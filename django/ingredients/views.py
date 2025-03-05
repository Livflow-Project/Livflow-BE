from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ingredient
from .serializers import IngredientSerializer
from inventory.models import Inventory  # ✅ Inventory 모델 추가
from inventory.serializers import InventorySerializer  # ✅ InventorySerializer 추가
import uuid

class StoreInventoryView(APIView):
    def get(self, request, store_id):
        """특정 상점의 재고 목록 조회 (unit_cost 포함)"""
        inventories = Inventory.objects.filter(ingredient__store_id=store_id)
        inventory_data = [
            {
                "ingredient_id": str(inv.ingredient.id),
                "ingredient_name": inv.ingredient.name,
                "remaining_stock": inv.remaining_stock,
                "unit": inv.unit,  # ✅ Ingredient에서 가져옴
                "unit_cost": inv.unit_cost,  # ✅ Ingredient에서 가져옴
            }
            for inv in inventories
        ]
        return Response(inventory_data, status=status.HTTP_200_OK)

    def post(self, request, store_id):
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
        """ 특정 재료 상세 조회 """
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, store_id, ingredient_id):
        """ 특정 재료 수정 """
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, store_id, ingredient_id):
        """ 특정 재료 삭제 """
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        ingredient.delete()
        return Response({"message": "재료가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
