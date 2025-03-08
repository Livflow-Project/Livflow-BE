from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ingredient
from inventory.models import Inventory  # ✅ Inventory 모델 사용
from .serializers import IngredientSerializer
from inventory.serializers import InventorySerializer

class StoreIngredientView(APIView):
    def get(self, request, store_id):
        """ 특정 상점의 모든 재료 조회 (Ingredient 기준) """
        ingredients = Ingredient.objects.filter(store_id=store_id)

        ingredient_data = [
            {
                "ingredient_id": str(ingredient.id),
                "ingredient_name": ingredient.name,
                "ingredient_cost": ingredient.purchase_price,
                "capacity": ingredient.purchase_quantity,  # ✅ 원래 등록된 구매 용량 기준
                "unit": ingredient.unit,
                "unit_cost": ingredient.unit_cost,  
                "shop": ingredient.vendor if ingredient.vendor else None,
                "ingredient_detail": ingredient.notes if ingredient.notes else None,
            }
            for ingredient in ingredients
        ]
        return Response(ingredient_data, status=status.HTTP_200_OK)


    def post(self, request, store_id):
        """특정 상점에 재료 추가"""
        data = request.data.copy()
        data["store"] = store_id  # ✅ store_id 직접 추가
        serializer = IngredientSerializer(data=data)

        if serializer.is_valid():
            ingredient = serializer.save()

            # ✅ Inventory 자동 추가 (초기 재고량 설정)
            Inventory.objects.create(
                ingredient=ingredient,
                remaining_stock=ingredient.purchase_quantity  # ✅ 최초 재고는 구매한 용량과 동일
            )

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

