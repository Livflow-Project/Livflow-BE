from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from .models import Store  
from ledger.models import Transaction 
from .serializers import StoreSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from django.db.models import Sum

class StoreListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="현재 로그인한 사용자의 모든 가게 조회",
        operation_description="사용자가 소유한 모든 가게와 해당 가게의 월별 차트 데이터를 반환합니다.",
        responses={200: "가게 목록과 차트 정보"}
    )    
    
    def get(self, request):
        """ 현재 로그인한 사용자의 모든 가게 목록 + 현재 월의 Ledger 차트 정보 포함 """
        stores = Store.objects.filter(user=request.user).order_by("created_at")
        response_data = []

        # 현재 연/월 기준
        now = datetime.now()
        target_year = now.year
        target_month = now.month

        for store in stores:
            # 수입(income) 상위 3개 카테고리
            income_transactions = Transaction.objects.filter(
                store=store, transaction_type="income",
                date__year=target_year, date__month=target_month
            ).values("transaction_type", "category__name").annotate(
                total=Sum("amount")
            ).order_by("-total")[:5]

            # 지출(expense) 상위 3개 카테고리
            expense_transactions = Transaction.objects.filter(
                store=store, transaction_type="expense",
                date__year=target_year, date__month=target_month
            ).values("transaction_type", "category__name").annotate(
                total=Sum("amount")
            ).order_by("-total")[:5]

            # 수입/지출 합쳐서 chart 데이터 생성
            transactions = list(income_transactions) + list(expense_transactions)

            chart_data = [
                {
                    "type": t["transaction_type"],
                    "category": t["category__name"] or "미분류",
                    "cost": float(t["total"])
                }
                for t in transactions
            ]

            # 최종 응답 데이터 구성
            response_data.append({
                "store_id": str(store.id),
                "name": store.name,
                "address": store.address,
                "chart": chart_data  # 현재 월 기준 차트
            })

        return Response({"stores": response_data}, status=status.HTTP_200_OK)



    @swagger_auto_schema(
        operation_summary="새 가게 등록",
        operation_description="새로운 가게를 등록합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='가게 이름'),
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='가게 주소 (선택)'),
            },
            required=['name'],
        ),
        responses={201: StoreSerializer(), 400: "유효성 검사 실패"}
    )
    def post(self, request):
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 가게 조회",
        operation_description="가게 ID를 이용해 해당 가게의 기본 정보를 조회합니다.",
        responses={200: StoreSerializer(), 404: "가게를 찾을 수 없습니다."}
    )
    def get(self, request, id):
        store = get_object_or_404(Store, id=id, user=request.user)
        return Response({
            "store_id": str(store.id),
            "name": store.name,
            "address": store.address
        })

    @swagger_auto_schema(
        operation_summary="가게 정보 수정",
        operation_description="가게 ID를 이용해 가게 정보를 수정합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='가게 이름'),
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='가게 주소 (선택)'),
            },
            required=['name'],
        ),
        responses={200: StoreSerializer(), 400: "유효성 검사 실패", 404: "가게를 찾을 수 없습니다."}
    )
    def put(self, request, id):
        store = get_object_or_404(Store, id=id, user=request.user)
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="가게 삭제",
        operation_description="가게 ID를 이용해 해당 가게를 삭제합니다.",
        responses={204: "가게 삭제 성공", 404: "가게를 찾을 수 없습니다."}
    )
    def delete(self, request, id):
        store = get_object_or_404(Store, id=id, user=request.user)
        store.delete()
        return Response({"message": "가게가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


