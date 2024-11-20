from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum

# 거래 내역 및 통계 조회 클래스
class TransactionSummaryView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # 로그인된 사용자의 거래 내역 조회
        transactions = Transaction.objects.filter(user_id=request.user.id)
        
        # 날짜별로 그룹화
        date_grouped = {}
        for transaction in transactions:
            date = transaction.date.strftime('%Y-%m-%d')
            if date not in date_grouped:
                date_grouped[date] = []
            date_grouped[date].append({
                "category": transaction.category.name,
                "transaction_type": transaction.transaction_type,
                "amount": transaction.amount,
                "description": transaction.description
            })

        # 날짜별 Top 5 지출/수입 계산
        top_5_by_date = {}
        for date, items in date_grouped.items():
            # 지출/수입을 각각 분리
            expenses = [item for item in items if item["transaction_type"] == "Expense"]
            incomes = [item for item in items if item["transaction_type"] == "Income"]

            # 금액을 기준으로 정렬 후 상위 5개 추출
            top_expenses = sorted(expenses, key=lambda x: x["amount"], reverse=True)[:5]
            top_incomes = sorted(incomes, key=lambda x: x["amount"], reverse=True)[:5]

            top_5_by_date[date] = {
                "top_expenses": top_expenses,
                "top_incomes": top_incomes
            }

        # 총 지출 및 총 수입 계산
        total_expenses = transactions.filter(transaction_type="Expense").aggregate(Sum("amount"))["amount__sum"] or 0
        total_incomes = transactions.filter(transaction_type="Income").aggregate(Sum("amount"))["amount__sum"] or 0

        # 최종 응답 데이터 구성
        response_data = {
            "detailed_transactions": date_grouped,
            "top_5_by_date": top_5_by_date,
            "total_expenses": total_expenses,
            "total_incomes": total_incomes
        }

        return Response(response_data, status=status.HTTP_200_OK)




# Transaction 상세 조회, 수정 및 삭제 클래스
class TransactionDetailView(APIView):
   #permission_classes = [IsAuthenticated]

    # 특정 거래 내역 조회
    def get(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user_id=request.user.id)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    # 특정 거래 내역 수정
    def put(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user_id=request.user.id)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 특정 거래 내역 삭제
    def delete(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user_id=request.user.id)
        transaction.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


# Category 목록 조회 및 생성 클래스
class CategoryView(APIView):
    #permission_classes = [IsAuthenticated]

    # 카테고리 목록 조회
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    # 카테고리 생성
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Category 상세 조회, 수정 및 삭제 클래스
class CategoryDetailView(APIView):
    #permission_classes = [IsAuthenticated]

    # 특정 카테고리 조회
    def get(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    # 특정 카테고리 수정
    def put(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 특정 카테고리 삭제
    def delete(self, request, id):
        category = get_object_or_404(Category, id=id)
        category.delete()
        return Response({"message": "카테고리가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
