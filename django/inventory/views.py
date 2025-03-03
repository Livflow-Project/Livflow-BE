from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Inventory
from .serializers import InventorySerializer

# ✅ 특정 상점의 재고 조회
class StoreInventoryView(APIView):
    def get(self, request, store_id):
        inventories = Inventory.objects.filter(ingredient__store_id=store_id)
        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ 특정 재료 사용 (재고 차감) 
class UseIngredientStockView(APIView):
    def post(self, request, store_id, ingredient_id):
        """ 특정 재료의 재고 사용 처리 """
        inventory = get_object_or_404(Inventory, ingredient__id=ingredient_id, ingredient__store_id=store_id)
        used_stock = request.data.get("used_stock")

        if not isinstance(used_stock, (int, float)) or used_stock <= 0:
            return Response({"error": "유효한 사용량(used_stock)을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        if inventory.remaining_stock < used_stock:
            return Response({"error": "남은 재고보다 많이 사용할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 남은 재고 차감
        inventory.remaining_stock -= used_stock
        inventory.save()

        return Response(
            {
                "ingredient_id": inventory.ingredient.id,
                "ingredient_name": inventory.ingredient.name,
                "remaining_stock": inventory.remaining_stock,  # ✅ 업데이트된 재고 값 반환
                "unit": inventory.ingredient.unit,
            },
            status=status.HTTP_200_OK,
        )
