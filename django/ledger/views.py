from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from store.models import Store, Transaction
from ledger.models import Category
from ledger.serializers import TransactionSerializer, CategorySerializer
from datetime import datetime
from django.db.models import Sum


# ✅ 1️⃣ 거래 내역 목록 조회 & 생성
class LedgerTransactionListCreateView(APIView):  
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id):
        """ ✅ 특정 상점의 모든 거래 내역 조회 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transactions = Transaction.objects.filter(store=store)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, store_id, transaction_id):
        """ ✅ 특정 거래 내역 수정 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)

        serializer = TransactionSerializer(transaction, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

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
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """ ✅ 새로운 카테고리 추가 """
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 4️⃣ 특정 카테고리 조회, 수정, 삭제 (`category_id`를 UUID로 변경)
class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category_id):
        """ ✅ 특정 카테고리 조회 """
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, category_id):
        """ ✅ 특정 카테고리 수정 """
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id):
        """ ✅ 특정 카테고리 삭제 """
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
    
    
    # ✅ 5️⃣ 특정 월의 거래 내역을 조회 (캘린더 API)
class LedgerCalendarView(APIView):  
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id):
        """ 특정 월의 거래 내역을 조회하여, 달력 & 차트 데이터 반환 """
        year = request.GET.get("year")
        month = request.GET.get("month")

        if not year or not month:
            return Response({"error": "year와 month 쿼리 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 상점 확인
        store = get_object_or_404(Store, id=store_id, user=request.user)

        # ✅ 해당 월의 모든 거래 조회
        transactions = Transaction.objects.filter(
            store=store,
            date__year=year,
            date__month=month
        )

        # ✅ 날짜별 수입/지출 여부 정리
        day_summary = {}
        for t in transactions:
            day = t.date.day
            if day not in day_summary:
                day_summary[day] = {"hasIncome": False, "hasExpense": False}

            if t.transaction_type == "income":
                day_summary[day]["hasIncome"] = True
            else:
                day_summary[day]["hasExpense"] = True

        days_list = [{"day": day, **summary} for day, summary in day_summary.items()]

        # ✅ 카테고리별 총 수입/지출 계산
        category_summary = transactions.values("transaction_type", "category__name").annotate(
            total=Sum("amount")
        ).order_by("-total")[:5]  # ✅ 상위 5개 카테고리만 반환

        category_data = [
            {"type": c["transaction_type"], "category": c["category__name"], "total": c["total"]}
            for c in category_summary
        ]

        # ✅ 최종 응답 데이터
        response_data = {
            "days": days_list,
            "chart": {
                "totalIncome": transactions.filter(transaction_type="income").aggregate(Sum("amount"))["amount__sum"] or 0,
                "totalExpense": transactions.filter(transaction_type="expense").aggregate(Sum("amount"))["amount__sum"] or 0,
                "categories": category_data,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)


# ✅ 6️⃣ 특정 날짜의 거래 내역 조회 (일별 거래 조회 API)
class LedgerDailyTransactionView(APIView):  
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id):
        """ 특정 날짜의 모든 거래 내역 조회 """
        year = request.GET.get("year")
        month = request.GET.get("month")
        day = request.GET.get("day")

        if not year or not month or not day:
            return Response({"error": "year, month, day 쿼리 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 상점 확인
        store = get_object_or_404(Store, id=store_id, user=request.user)

        # ✅ 해당 날짜의 거래 내역 조회
        transactions = Transaction.objects.filter(
            store=store,
            date__year=year,
            date__month=month,
            date__day=day
        )

        # ✅ 거래 내역을 JSON 형태로 변환
        transaction_list = [
            {
                "transaction_id": str(t.id),
                "type": t.transaction_type,
                "category": t.category.name,
                "detail": t.description or "",
                "cost": t.amount
            }
            for t in transactions
        ]

        return Response(transaction_list, status=status.HTTP_200_OK)
