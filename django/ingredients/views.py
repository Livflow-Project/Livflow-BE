from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ingredient
from .serializers import IngredientSerializer
from .utils import calculate_unit_price  # ✅ 이제 실제로 활용!

# ✅ 특정 상점의 모든 재료 조회 (GET) + 특정 재료 등록 (POST)
class StoreInventoryView(APIView):
    def get(self, request, store_id):
        ingredients = Ingredient.objects.filter(store_id=store_id)
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, store_id):
        data = request.data.copy()
        data["store"] = store_id
        # ✅ unit_cost 자동 계산 후 추가
        data["unit_cost"] = calculate_unit_price(data["purchase_price"], data["purchase_quantity"])
        
        serializer = IngredientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ 특정 재료 수정 (PUT & PATCH 지원)
class IngredientUpdateView(APIView):
    def put(self, request, store_id, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        data = request.data.copy()
        # ✅ unit_cost 자동 계산 후 추가
        data["unit_cost"] = calculate_unit_price(data["purchase_price"], data["purchase_quantity"])

        serializer = IngredientSerializer(ingredient, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, store_id, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        data = request.data.copy()
        # ✅ unit_cost 자동 계산 (PATCH에서도 적용)
        if "purchase_price" in data and "purchase_quantity" in data:
            data["unit_cost"] = calculate_unit_price(data["purchase_price"], data["purchase_quantity"])

        serializer = IngredientSerializer(ingredient, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
