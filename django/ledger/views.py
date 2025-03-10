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
from datetime import date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# ✅ 1️⃣ 거래 내역 목록 조회 & 생성
class LedgerTransactionListCreateView(APIView):  
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="특정 상점의 모든 거래 내역 조회",
        responses={200: TransactionSerializer(many=True)}
    )    

    def get(self, request, store_id):
        """ ✅ 특정 상점의 모든 거래 내역 조회 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transactions = Transaction.objects.filter(store=store)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="거래 내역 생성",
        request_body=TransactionSerializer,
        responses={201: TransactionSerializer()}
    )

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
    
    @swagger_auto_schema(
        operation_summary="특정 거래 내역 조회",
        responses={200: TransactionSerializer()}
    )    

    def get(self, request, store_id, transaction_id):
        """ ✅ 특정 거래 내역 조회 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="특정 거래 내역 수정",
        request_body=TransactionSerializer,
        responses={200: TransactionSerializer()}
    )

    def put(self, request, store_id, transaction_id):
        """ ✅ 특정 거래 내역 수정 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)

        # 🔥 요청 데이터 복사 후 category 처리
        data = request.data.copy()
        
        category_input = data.get("category")  # ✅ category 값 확인

        if category_input:
            if category_input.isdigit():  
                # ✅ 숫자이면 기존 Category ID로 조회
                category = get_object_or_404(Category, id=int(category_input))
            else:
                # ✅ 문자열이면 카테고리명으로 조회 or 생성
                category, _ = Category.objects.get_or_create(name=category_input)

            data["category"] = category.id  # ✅ ForeignKey에는 ID 저장

        serializer = TransactionSerializer(transaction, data=data, partial=True, context={"request": request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="특정 거래 내역 삭제",
        responses={204: "삭제 완료"}
    )

    def delete(self, request, store_id, transaction_id):
        """ ✅ 특정 거래 내역 삭제 """
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, store=store)
        transaction.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


# ✅ 3️⃣ 카테고리 목록 조회 & 생성
class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 월의 거래 내역 조회",
        manual_parameters=[
            openapi.Parameter("year", openapi.IN_QUERY, description="조회할 연도", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter("month", openapi.IN_QUERY, description="조회할 월", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={200: "캘린더 및 차트 데이터 반환"}
    )

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

    @swagger_auto_schema(
        operation_summary="특정 월의 거래 내역 조회",
        manual_parameters=[
            openapi.Parameter("year", openapi.IN_QUERY, description="조회할 연도", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter("month", openapi.IN_QUERY, description="조회할 월", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={200: "캘린더 및 차트 데이터 반환"}
    )

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

        # ✅ 카테고리별 총 수입/지출 계산 (🚨 `ledger.models.Category` 참조)
        category_summary = transactions.values("transaction_type", "category__name").annotate(
            total=Sum("amount")
        ).order_by("-total")[:5]  # ✅ 상위 5개 카테고리만 반환

        category_data = [
            {
                "type": c["transaction_type"],
                "category": c["category__name"] if c["category__name"] else "미분류",  # ✅ 카테고리 없으면 "미분류"
                "total": float(c["total"])  # ✅ Decimal → float 변환
            }
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



class LedgerDailyTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 날짜의 거래 내역 조회",
        manual_parameters=[
            openapi.Parameter("year", openapi.IN_QUERY, description="조회할 연도", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter("month", openapi.IN_QUERY, description="조회할 월", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter("day", openapi.IN_QUERY, description="조회할 일", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={200: "거래 내역 리스트 반환"}
    )

    def get(self, request, store_id):
        """ ✅ 특정 날짜의 거래 내역 조회 (요청된 형식에 맞게 수정) """
        year = request.GET.get("year")
        month = request.GET.get("month")
        day = request.GET.get("day")

        if not year or not month or not day:
            return Response({"error": "year, month, day 쿼리 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        store = get_object_or_404(Store, id=store_id, user=request.user)

        try:
            target_date = date(int(year), int(month), int(day))  # 🔥 날짜 변환 명확하게 처리
        except ValueError:
            return Response({"error": "올바른 날짜를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        transactions = Transaction.objects.filter(store=store, date=target_date)

        response_data = [
            {
                "transaction_id": str(t.id),  # ✅ `id` → `transaction_id`
                "type": t.transaction_type,
                "category": t.category.name if t.category else "미분류",  # ✅ 카테고리가 없으면 기본값 처리
                "detail": t.description or "",
                "cost": float(t.amount)  # ✅ Decimal을 float으로 변환
            }
            for t in transactions
        ]

        return Response(response_data, status=status.HTTP_200_OK)

