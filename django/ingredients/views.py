from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ingredient
from .serializers import IngredientSerializer

# ✅ 특정 상점의 모든 재료 조회 (GET) + 특정 재료 등록 (POST)
class StoreInventoryView(APIView):
    def get(self, request, store_id):
        ingredients = Ingredient.objects.filter(store_id=store_id)
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, store_id):
        data = request.data.copy()
        data["store"] = store_id
        serializer = IngredientSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ✅ 특정 재료 상세 조회
class IngredientDetailView(APIView):
    def get(self, request, store_id, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ 특정 재료 수정 (PUT & PATCH 지원)
class IngredientUpdateView(APIView):
    def put(self, request, store_id, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=False)  # 전체 업데이트 (PUT)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, store_id, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)  # 부분 업데이트 (PATCH)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ✅ 특정 재료 삭제
class IngredientDeleteView(APIView):
    def delete(self, request, store_id, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id, store_id=store_id)
        ingredient.delete()
        return Response({"message": "재료가 삭제되었습니다."}, status=status.HTTP_200_OK)  # ✅ HTTP 200 OK로 변경
