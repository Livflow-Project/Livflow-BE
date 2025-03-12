from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from store.models import Store  
from ledger.models import Transaction
from ledger.models import Category
from ledger.serializers import TransactionSerializer, CategorySerializer
from datetime import datetime
from django.db.models import Sum
from datetime import date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction


# ✅ 1️⃣ 거래 내역 목록 조회 & 생성
class LedgerTransactionListCreateView(APIView):  
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="특정 상점의 모든 거래 내역 조회",
        responses={200: TransactionSerializer(many=True)}
    )    
#'<uuid:store_id>/transactions/
    def get(self, request, store_id):
        store = get_object_or_404(Store, id=store_id, user=request.user)

        year = request.GET.get("year")
        month = request.GET.get("month")
        day = request.GET.get("day")

        print(f"📌 [DEBUG] 요청된 파라미터 - year: {year}, month: {month}, day: {day}")

        try:
            year = int(year)
            month = int(month)
            day = int(day) if day else None
        except ValueError:
            return Response({"error": "year, month, day는 숫자여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ ledger.models.Transaction을 조회하도록 변경
        transactions = Transaction.objects.filter(store=store, date__year=year, date__month=month)
        if day:
            transactions = transactions.filter(date__day=day)

        print(f"📌 [DEBUG] SQL Query: {transactions.query}")  
        print(f"📌 [DEBUG] 필터링된 거래 개수: {transactions.count()}")  

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    @swagger_auto_schema(
        operation_summary="거래 내역 생성",
        request_body=TransactionSerializer,
        responses={201: TransactionSerializer()}
    )

#/ledger/{storeId}/transactions


    def post(self, request, store_id):
        """ ✅ 거래 내역 생성 (트랜잭션 강제 커밋 추가) """
        data = request.data.copy()
        data["store_id"] = str(store_id)  # 🔹 store_id 추가

        serializer = TransactionSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            try:
                with transaction.atomic():  # ✅ 트랜잭션 강제 적용
                    transaction_obj = serializer.save()

                    # ✅ DB에 즉시 반영 확인
                    transaction_obj.refresh_from_db()
                    print(f"📌 [DEBUG] 저장된 Transaction - ID: {transaction_obj.id}, 날짜: {transaction_obj.date}")

                    # ✅ 저장 후 즉시 DB에서 다시 조회
                    db_check = Transaction.objects.filter(id=transaction_obj.id).exists()
                    if not db_check:
                        print(f"⚠️ [ERROR] `ledger_transaction` 테이블이 아니라 다른 테이블에 저장되었을 가능성 있음!")

                return Response(TransactionSerializer(transaction_obj).data, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f"⚠️ [ERROR] 트랜잭션 저장 실패: {e}")
                return Response({"error": "트랜잭션 저장 중 오류 발생"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# ✅ 2️⃣ 특정 거래 내역 조회, 수정, 삭제
class LedgerTransactionDetailView(APIView):  
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="특정 거래 내역 조회",
        responses={200: TransactionSerializer()}
    )    
    
#<uuid:store_id>/transactions/<uuid:transaction_id>/
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

#/ledger/{storeId}/transactions/{transactionId}
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

    @swagger_auto_schema(
        operation_summary="새로운 카테고리 추가",
        request_body=CategorySerializer,
        responses={201: CategorySerializer(), 400: "유효성 검사 실패"}
    )


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

    @swagger_auto_schema(
        operation_summary="특정 카테고리 조회",
        responses={200: CategorySerializer()}
    )

    def get(self, request, category_id):
        """ ✅ 특정 카테고리 조회 """
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="특정 카테고리 수정",
        request_body=CategorySerializer,
        responses={200: CategorySerializer(), 400: "유효성 검사 실패"}
    )

    def put(self, request, category_id):
        """ ✅ 특정 카테고리 수정 """
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="특정 카테고리 삭제",
        responses={204: "삭제 완료"}
    )

    def delete(self, request, category_id):
        """ ✅ 특정 카테고리 삭제 """
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

#'<uuid:store_id>/calendar/'
class LedgerCalendarView(APIView):  
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 월 또는 특정 날짜의 거래 내역 조회",
        manual_parameters=[
            openapi.Parameter("year", openapi.IN_QUERY, description="조회할 연도", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter("month", openapi.IN_QUERY, description="조회할 월", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter("day", openapi.IN_QUERY, description="조회할 일", type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={200: "달력 & 차트 데이터 반환"}
    )

    def get(self, request, store_id):
        print("🚀🚀🚀 GET 요청이 들어왔습니다!") 
        
        year = request.GET.get("year")
        month = request.GET.get("month")
        day = request.GET.get("day")  # ✅ day 추가

        print(f"📌 [DEBUG] 요청된 파라미터 - year: {year}, month: {month}, day: {day}")  # ✅ 입력값 확인

        if not year or not month:
            return Response({"error": "year와 month 쿼리 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response({"error": "year와 month는 필수 값이며, 숫자여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)


        # ✅ 상점 확인
        store = get_object_or_404(Store, id=store_id, user=request.user)

        # ✅ 거래 필터링
        filters = {"store": store, "date__year": year, "date__month": month}
        if day:
            filters["date__day"] = day  # ✅ day 필터 추가

        transactions = Transaction.objects.filter(**filters)

        print(f"📌 [DEBUG] SQL Query: {transactions.query}")  # ✅ 실제 SQL 확인
        print(f"📌 [DEBUG] 필터링된 거래 개수: {transactions.count()}")  # ✅ 데이터 개수 확인
        print(f"📌 [DEBUG] 필터링된 거래 목록: {list(transactions.values('date', 'amount', 'transaction_type'))}")  # ✅ 실제 데이터 확인

        if day:
            # ✅ 특정 날짜의 거래 내역 응답
            response_data = [
                {
                    "transaction_id": str(t.id),
                    "type": t.transaction_type,
                    "category": t.category.name if t.category else "미분류",
                    "detail": t.description or "",
                    "cost": float(t.amount)
                }
                for t in transactions
            ]
        else:
            # ✅ 특정 월의 달력 & 차트 데이터 응답
            day_summary = {}
            for t in transactions:
                trans_day = t.date.day
                if trans_day not in day_summary:
                    day_summary[trans_day] = {"hasIncome": False, "hasExpense": False}

                if t.transaction_type == "income":
                    day_summary[trans_day]["hasIncome"] = True
                else:
                    day_summary[trans_day]["hasExpense"] = True

            days_list = [{"day": d, **summary} for d, summary in day_summary.items()]

            category_summary = transactions.values("transaction_type", "category__name").annotate(
                total=Sum("amount")
            ).order_by("-total")[:5]

            category_data = [
                {
                    "type": c["transaction_type"],
                    "category": c["category__name"] if c["category__name"] else "미분류",
                    "total": float(c["total"])
                }
                for c in category_summary
            ]

            response_data = {
                "days": days_list,
                "chart": {
                    "totalIncome": transactions.filter(transaction_type="income").aggregate(Sum("amount"))["amount__sum"] or 0,
                    "totalExpense": transactions.filter(transaction_type="expense").aggregate(Sum("amount"))["amount__sum"] or 0,
                    "categories": category_data,
                }
            }

        return Response(response_data, status=status.HTTP_200_OK)


