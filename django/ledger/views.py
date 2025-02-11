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


# 거래 내역 목록 조회 및 생성 클래스
class TransactionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="거래 내역 목록 조회",
        responses={200: TransactionSerializer(many=True)},
    )
    def get(self, request, store_id):
        store = get_object_or_404(Store, id=store_id, user=request.user)  # ✅ 특정 유저의 가게인지 확인
        transactions = Transaction.objects.filter(store=store)  # ✅ 특정 가게의 거래만 가져오기
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
        store = get_object_or_404(Store, id=store_id, user=request.user)  # ✅ store_id 추가

        transaction_data = {
            "user": request.user.id,
            "store": store.id,  # ✅ store 추가
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



# 특정 거래 내역 조회, 수정 및 삭제 클래스
class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 거래 내역 조회",
        responses={200: TransactionSerializer, 404: "거래 내역을 찾을 수 없음"},
    )
    def get(self, request, store_id, id):
        store = get_object_or_404(Store, id=store_id, user=request.user)  # ✅ store 확인
        transaction = get_object_or_404(Transaction, id=id, store=store)  # ✅ store 기준 필터링
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="특정 거래 내역 수정",
        request_body=TransactionSerializer,
        responses={200: TransactionSerializer, 400: "잘못된 요청 데이터", 404: "거래 내역을 찾을 수 없음"},
    )
    def put(self, request, store_id, id):
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=id, store=store)  # ✅ 해당 store의 거래인지 확인

        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="특정 거래 내역 삭제",
        responses={204: "삭제 성공", 404: "거래 내역을 찾을 수 없음"},
    )
    def delete(self, request, store_id, id):
        store = get_object_or_404(Store, id=store_id, user=request.user)
        transaction = get_object_or_404(Transaction, id=id, store=store)  # ✅ store 기준 필터링
        transaction.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

# 카테고리 목록 조회 및 생성 클래스
class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="카테고리 목록 조회",
        responses={200: CategorySerializer(many=True)},
    )
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="카테고리 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='카테고리 이름'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='카테고리 설명'),
            },
            required=['name'],
        ),
        responses={201: CategorySerializer, 400: "잘못된 요청 데이터"},
    )
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 특정 카테고리 조회, 수정 및 삭제 클래스
class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 카테고리 조회",
        responses={200: CategorySerializer, 404: "카테고리를 찾을 수 없음"},
    )
    def get(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="특정 카테고리 수정",
        request_body=CategorySerializer,
        responses={200: CategorySerializer, 400: "잘못된 요청 데이터", 404: "카테고리를 찾을 수 없음"},
    )
    def put(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="특정 카테고리 삭제",
        responses={204: "삭제 성공", 404: "카테고리를 찾을 수 없음"},
    )
    def delete(self, request, id):
        category = get_object_or_404(Category, id=id)
        category.delete()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)




# 1️⃣ 월별 차트 및 거래 여부 조회
class LedgerCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="가게 월별 차트 및 거래 여부 조회",
        operation_description="월별 총 수입, 지출 금액과 각 날짜별 거래 여부를 반환합니다.",
        manual_parameters=[
            openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: "월별 차트 및 거래 여부 반환", 404: "가게를 찾을 수 없습니다."}
    )
    def get(self, request, storeId):
        year = request.GET.get('year')
        month = request.GET.get('month')

        if not year or not month or not year.isdigit() or not month.isdigit():
            return Response({"detail": "year와 month는 숫자여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        year, month = int(year), int(month)

        store = get_object_or_404(Store, id=storeId, user=request.user)

        # 월별 수입/지출 차트 데이터
        chart_data = Transaction.objects.filter(store=store, date__year=year, date__month=month)\
            .values('transaction_type').annotate(total=Sum('amount'))

        chart = [{"type": t["transaction_type"], "total": t["total"]} for t in chart_data]

        # 일별 거래 여부
        date_data = Transaction.objects.filter(store=store, date__year=year, date__month=month)\
            .values('date__day').annotate(count=Count('id'))

        date_info = [{"day": d["date__day"], "has_transaction": d["count"] > 0} for d in date_data]

        return Response({"chart": chart, "date_info": date_info}, status=status.HTTP_200_OK)


# 2️⃣ 특정 날짜 거래 내역 조회
class LedgerTransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 날짜 거래 내역 조회",
        operation_description="가게 ID와 날짜를 입력하여 해당 일의 수입, 지출 내역을 조회합니다.",
        manual_parameters=[
            openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('day', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: "거래 내역 반환", 404: "가게를 찾을 수 없습니다."}
    )
    def get(self, request, storeId):
        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')

        if not year or not month or not day or not year.isdigit() or not month.isdigit() or not day.isdigit():
            return Response({"detail": "year, month, day는 숫자여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        year, month, day = int(year), int(month), int(day)

        store = get_object_or_404(Store, id=storeId, user=request.user)

        transactions = Transaction.objects.filter(store=store, date__year=year, date__month=month, date__day=day)\
            .values('id', 'transaction_type', 'category__name', 'description', 'amount')

        response_data = {
            "date": f"{year}-{month:02d}-{day:02d}",
            "transactions": [
                {
                    "transaction_id": str(t['id']),
                    "type": t['transaction_type'],
                    "category": t['category__name'],
                    "detail": t['description'],
                    "cost": t['amount']
                } for t in transactions
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)
