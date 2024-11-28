from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Store
from .serializers import StoreSerializer
from ledger.models import Transaction
from ledger.serializers import TransactionSerializer

# 모든 가게 목록 조회 및 새로운 가게 등록
class StoreListView(APIView):
    # permission_classes = [IsAuthenticated]

    # 모든 가게 목록 조회
    def get(self, request):
        stores = Store.objects.filter(user_id=request.user.id)
        store_list = []

        for store in stores:
            store_serializer = StoreSerializer(store)

            # 가계부 정보 가져오기 (수입/지출을 카테고리별로 합산)
            transactions = Transaction.objects.filter(user_id=request.user.id, store_id=store.id)
            income_totals = {}
            expense_totals = {}

            for transaction in transactions:
                category_name = transaction.category.name
                if transaction.transaction_type == "income":
                    income_totals[category_name] = income_totals.get(category_name, 0) + transaction.amount
                elif transaction.transaction_type == "expense":
                    expense_totals[category_name] = expense_totals.get(category_name, 0) + transaction.amount

            store_data = {
                "store": store_serializer.data,
                "category_totals": {
                    "income": income_totals,
                    "expense": expense_totals,
                }
            }

            store_list.append(store_data)

        return Response(store_list)

    # 새로운 가게 등록
    def post(self, request):
        store_data = {
            "name": request.data.get("name"),
            "address": request.data.get("address")
        }
        serializer = StoreSerializer(data=store_data)
        
        if serializer.is_valid():
            # Store 인스턴스 생성 시 user를 자동으로 추가
            serializer.save(user=request.user)  # 인증된 사용자로 user 필드를 설정
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 특정 가게 조회, 수정 및 삭제 클래스
class StoreDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    # 특정 가게 조회 (가계부 정보 포함)
    def get(self, request, id):
        try:
            store = Store.objects.get(id=id, user_id=request.user.id)
        except Store.DoesNotExist:
            return Response({"detail": "해당 가게를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        store_serializer = StoreSerializer(store)

        # 가계부 정보 가져오기 (수입/지출을 카테고리별로 합산)
        transactions = Transaction.objects.filter(user_id=request.user.id, store_id=id)
        income_totals = {}
        expense_totals = {}
        
        for transaction in transactions:
            category_name = transaction.category.name
            if transaction.transaction_type == "income":
                income_totals[category_name] = income_totals.get(category_name, 0) + transaction.amount
            elif transaction.transaction_type == "expense":
                expense_totals[category_name] = expense_totals.get(category_name, 0) + transaction.amount

        store_data = {
            "store": store_serializer.data,
            "category_totals": {
                "income": income_totals,
                "expense": expense_totals,
            }
        }
        return Response(store_data)

    # 가게 정보 수정
    def put(self, request, id):
        try:
            store = Store.objects.get(id=id, user_id=request.user.id)
        except Store.DoesNotExist:
            return Response({"detail": "해당 가게를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        data = {
            "name": request.data.get("name"),
            "address": request.data.get("address")
        }
        serializer = StoreSerializer(store, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 가게 삭제
    def delete(self, request, id):
        try:
            store = Store.objects.get(id=id, user_id=request.user.id)
        except Store.DoesNotExist:
            return Response({"detail": "해당 가게를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        store.delete()
        return Response({"message": "가게가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
