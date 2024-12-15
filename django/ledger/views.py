from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

# Transaction 관련 처리 클래스
class TransactionView(APIView):
    permission_classes = [IsAuthenticated]
    # 거래 내역 목록 조회 및 거래 내역 생성
    def get(self, request):
        transactions = Transaction.objects.filter(user_id=request.user.id)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    def post(self, request):
        transaction_data = {
            "user_id": request.user.id,
            "category": request.data.get("category"),
            "transaction_type": request.data.get("transaction_type"),
            "amount": request.data.get("amount"),
            "remarks": request.data.get("remarks")
        }
        serializer = TransactionSerializer(data=transaction_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # 특정 거래 내역 조회, 수정 및 삭제
    def get_detail(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user_id=request.user.id)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)
    def put(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user_id=request.user.id)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user_id=request.user.id)
        transaction.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
# Category 관련 처리 클래스
class CategoryView(APIView):
    permission_classes = [IsAuthenticated]
    # 카테고리 목록 조회 및 카테고리 생성
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
    # 특정 카테고리 조회, 수정 및 삭제
    def get_detail(self, request, id):
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
        return Response({"message": "카테고리가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)