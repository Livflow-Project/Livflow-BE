from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Ingredient, Recipe, RecipeItem
from .serializers import IngredientSerializer, RecipeSerializer, RecipeItemSerializer
from .utils import calculate_unit_price, calculate_recipe_cost  # utils에서 계산 함수 가져오기

# 재료 관련 클래스
class IngredientView(APIView):
    permission_classes = [IsAuthenticated]

    # 모든 재료 목록 조회
    def get(self, request):
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)

    # 새로운 재료 생성
    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 특정 재료 조회, 수정, 삭제
    def get_detail(self, request, id):
        ingredient = get_object_or_404(Ingredient, id=id)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)

    def put(self, request, id):
        ingredient = get_object_or_404(Ingredient, id=id)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        ingredient = get_object_or_404(Ingredient, id=id)
        ingredient.delete()
        return Response({"message": "재료가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


# 레시피 및 레시피 재료 관련 클래스
class RecipeView(APIView):
    permission_classes = [IsAuthenticated]

    # 모든 레시피 목록 조회 및 새로운 레시피 생성
    def get(self, request):
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

    # 새로운 레시피 생성 및 비용 계산
    def post(self, request):
        # 레시피 생성 처리
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # 요청된 재료 리스트 가져오기
            ingredients = request.data.get('ingredients')  # 재료 정보는 리스트로 입력
            sales_price_per_item = request.data.get('sales_price_per_item')
            production_quantity_per_batch = request.data.get('production_quantity_per_batch')

            # 각 재료의 단가 계산 (구매가 / 구매용량)
            for ingredient in ingredients:
                ingredient_instance = get_object_or_404(Ingredient, id=ingredient['ingredient_id'])
                ingredient['unit_price'] = calculate_unit_price(ingredient_instance.purchase_price, ingredient_instance.purchase_quantity)

            # 레시피 원가 관련 정보 계산
            recipe_cost_data = calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch)

            # 반환 데이터 구성
            response_data = {
                "recipe": serializer.data,
                "cost_details": recipe_cost_data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 특정 레시피 조회, 수정, 삭제
    def get_detail(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)

    def put(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        recipe.delete()
        return Response({"message": "레시피가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

    # 레시피 재료 생성 및 조회
    def post_recipe_item(self, request):
        serializer = RecipeItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_recipe_items(self, request):
        recipe_items = RecipeItem.objects.all()
        serializer = RecipeItemSerializer(recipe_items, many=True)
        return Response(serializer.data)
