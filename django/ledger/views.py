from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Sum, Count

from store.models import Store, Transaction  
from .models import Category
from .serializers import TransactionSerializer, CategorySerializer


# 🔹 1️⃣ 거래 내역 목록 조회 & 생성
class LedgerTransactionListCreateView(APIView):  
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="거래 내역 목록 조회",
        responses={200: TransactionSerializer(many=True)},
    )
    def get(self, request, store_id):
        store = get_object_or_404(Store, id=store_id, user=request.user)  
        transactions = Transaction.objects.filter(store=store)  
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="거래 내역 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='카테고리 ID'),
                'transaction_type': openapi.Schema(type=openapi.TYPE_STRING, description='거래 유형 (예: income, expense)'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='거래 금액'),
                'date': openapi.Schema(type=openapi.FORMAT_DATE, description='거래 날짜 (YYYY-MM-DD)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='거래 설명 (선택 사항)'),
            },
            required=['category_id', 'transaction_type', 'amount', 'date'],
        ),
        responses={201: TransactionSerializer, 400: "잘못된 요청 데이터"},
    )
    def post(self, request, store_id):
        store = get_object_or_404(Store, id=store_id, user=request.user)  

        transaction_data = {
            "user": request.user.id,
            "store": store.id,  
            "category": request.data.get("category_id"),
            "transaction_type": request.data.get("transaction_type"),
            "amount": request.data.get("amount"),
            "date": request.data.get("date"),
            "description": request.data.get("description")
        }
        serializer = TransactionSerializer(data=transaction_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 2️⃣ 특정 거래 내역 조회, 수정, 삭제
class LedgerTransactionDetailView(APIView):  
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 거래 내역 조회",
        responses={200: TransactionSerializer, 404: "거래 내역을 찾을 수 없음"},
    )
    def get(self, request, store_id, transaction_id):
        store = get_object_or_404(Store, id=store_id, user=request.user)  
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)  
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="특정 거래 내역 수정",
        request_body=TransactionSerializer,
        responses={200: TransactionSerializer, 400: "잘못된 요청 데이터", 404: "거래 내역을 찾을 수 없음"},
    )
    def put(self, request, store_id, transaction_id):
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)  

        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="특정 거래 내역 삭제",
        responses={204: "삭제 성공", 404: "거래 내역을 찾을 수 없음"},
    )
    def delete(self, request, store_id, transaction_id):
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)  
        transaction.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

# 🔹 4️⃣ 카테고리 목록 조회 & 생성
class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 5️⃣ 특정 카테고리 조회, 수정, 삭제
class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        category = get_object_or_404(Category, id=id)
        category.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
