from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import datetime
from store.models import Store, Transaction
from ledger.models import Category
from ledger.serializers import TransactionSerializer, CategorySerializer


# ✅ 1️⃣ 거래 내역 목록 조회 & 생성
class LedgerTransactionListCreateView(APIView):  
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id):
        """ ✅ 특정 상점의 모든 거래 내역 조회 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transactions = Transaction.objects.filter(store=store)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request, store_id):
        """ ✅ 거래 내역 생성 """
        data = request.data.copy()
        data["store_id"] = str(store_id)  # 🔹 store_id 추가

        serializer = TransactionSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            transaction = serializer.save()
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 2️⃣ 특정 거래 내역 조회, 수정, 삭제
class LedgerTransactionDetailView(APIView):  
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id, transaction_id):
        """ ✅ 특정 거래 내역 조회 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    def put(self, request, store_id, transaction_id):
        """ ✅ 특정 거래 내역 수정 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)

        serializer = TransactionSerializer(transaction, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, store_id, transaction_id):
        """ ✅ 특정 거래 내역 삭제 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)
        transaction.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


# ✅ 3️⃣ 카테고리 목록 조회 & 생성
class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ ✅ 모든 카테고리 목록 조회 """
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        """ ✅ 새로운 카테고리 추가 """
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 4️⃣ 특정 카테고리 조회, 수정, 삭제
class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """ ✅ 특정 카테고리 조회 """
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, id):
        """ ✅ 특정 카테고리 수정 """
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """ ✅ 특정 카테고리 삭제 """
        category = get_object_or_404(Category, id=id)
        category.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
