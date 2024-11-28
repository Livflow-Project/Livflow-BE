from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Ingredient, Recipe, RecipeItem
from .serializers import IngredientSerializer, RecipeSerializer, RecipeItemSerializer
from .utils import calculate_unit_price, calculate_recipe_cost  # utils에서 계산 함수 가져오기

# 모든 재료 목록 조회 및 생성 클래스
class IngredientListView(APIView):
    # permission_classes = [IsAuthenticated]

    # 모든 재료 목록 조회
    def get(self, request):
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='재료 이름'),
                'purchase_price': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='구매 가격'),
                'purchase_quantity': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='구매 수량'),
                'unit': openapi.Schema(type=openapi.TYPE_STRING, description='단위 (예: g, ml, ea 등)'),
            },
            required=['name', 'purchase_price', 'purchase_quantity', 'unit'],
        )
    )
    # 새로운 재료 생성
    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 특정 재료 조회, 수정 및 삭제 클래스
class IngredientDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    # 특정 재료 조회
    def get(self, request, id):
        try:
            ingredient = Ingredient.objects.get(id=id)
        except Ingredient.DoesNotExist:
            return Response({"detail": "해당 재료를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='재료 이름'),
                'purchase_price': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='구매 가격'),
                'purchase_quantity': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='구매 수량'),
                'unit': openapi.Schema(type=openapi.TYPE_STRING, description='단위 (예: g, ml, ea 등)'),
            },
            required=['name', 'purchase_price', 'purchase_quantity', 'unit'],
        )
    )
    # 특정 재료 수정
    def put(self, request, id):
        try:
            ingredient = Ingredient.objects.get(id=id)
        except Ingredient.DoesNotExist:
            return Response({"detail": "해당 재료를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 특정 재료 삭제
    def delete(self, request, id):
        try:
            ingredient = Ingredient.objects.get(id=id)
        except Ingredient.DoesNotExist:
            return Response({"detail": "해당 재료를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        ingredient.delete()
        return Response({"message": "재료가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

# 레시피 목록 조회 및 생성 클래스
class RecipeListView(APIView):
    # permission_classes = [IsAuthenticated]

    # 모든 레시피 목록 조회
    def get(self, request):
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='레시피 이름'),
                'sales_price_per_item': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='항목당 판매 가격'),
                'production_quantity_per_batch': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='배치당 생산 수량'),
                'ingredients': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'ingredient_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='재료 ID'),
                            'quantity_used': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='사용된 수량'),
                            'unit': openapi.Schema(type=openapi.TYPE_STRING, description='단위 (예: g, ml, ea 등)'),
                        },
                        required=['ingredient_id', 'quantity_used', 'unit']
                    )
                )
            },
            required=['name', 'sales_price_per_item', 'production_quantity_per_batch', 'ingredients'],
        )
    )
    # 새로운 레시피 생성 및 비용 계산
    def post(self, request):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # 요청된 재료 리스트 가져오기
            ingredients = request.data.get('ingredients')
            sales_price_per_item = request.data.get('sales_price_per_item')
            production_quantity_per_batch = request.data.get('production_quantity_per_batch')

            # 각 재료의 단가 계산
            for ingredient in ingredients:
                try:
                    ingredient_instance = Ingredient.objects.get(id=ingredient['ingredient_id'])
                except Ingredient.DoesNotExist:
                    return Response({"detail": "해당 재료를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
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

# 특정 레시피 조회, 수정 및 삭제 클래스
class RecipeDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    # 특정 레시피 조회
    def get(self, request, id):
        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            return Response({"detail": "해당 레시피를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='레시피 이름'),
                'sales_price_per_item': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='항목당 판매 가격'),
                'production_quantity_per_batch': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='배치당 생산 수량'),
                'ingredients': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'ingredient_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='재료 ID'),
                            'quantity_used': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='사용된 수량'),
                            'unit': openapi.Schema(type=openapi.TYPE_STRING, description='단위 (예: g, ml, ea 등)'),
                        },
                        required=['ingredient_id', 'quantity_used', 'unit']
                    )
                )
            },
            required=['name', 'sales_price_per_item', 'production_quantity_per_batch', 'ingredients'],
        )
    )
    # 특정 레시피 수정
    def put(self, request, id):
        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            return Response({"detail": "해당 레시피를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 특정 레시피 삭제
    def delete(self, request, id):
        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            return Response({"detail": "해당 레시피를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        recipe.delete()
        return Response({"message": "레시피가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

# 레시피 재료 생성 클래스
class RecipeItemCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'recipe': openapi.Schema(type=openapi.TYPE_INTEGER, description='레시피 ID'),
                'ingredient': openapi.Schema(type=openapi.TYPE_INTEGER, description='재료 ID'),
                'quantity_used': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='사용된 수량'),
                'unit': openapi.Schema(type=openapi.TYPE_STRING, description='단위 (예: g, ml, ea 등)'),
            },
            required=['recipe', 'ingredient', 'quantity_used', 'unit'],
        )
    )
    def post(self, request):
        serializer = RecipeItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 레시피 재료 목록 조회 클래스
class RecipeItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recipe_items = RecipeItem.objects.all()
        serializer = RecipeItemSerializer(recipe_items, many=True)
        return Response(serializer.data)
