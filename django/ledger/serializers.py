from rest_framework import serializers
from django.shortcuts import get_object_or_404
from store.models import Transaction, Store
from ledger.models import Category
from datetime import datetime

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class TransactionSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(write_only=True)  # 🔹 store_id 직접 받기
    category = serializers.CharField(source="category.name", read_only=True)  # 🔹 카테고리 이름 반환
    category_id = serializers.UUIDField(write_only=True)  # 🔹 카테고리 ID 요청에서 받음
    date = serializers.SerializerMethodField()
    cost = serializers.DecimalField(source="amount", max_digits=10, decimal_places=2)
    type = serializers.CharField(source="transaction_type")
    detail = serializers.CharField(source="description", required=False)  # 🔹 description -> detail로 변환

    class Meta:
        model = Transaction
        fields = ["id", "store_id", "type", "category", "category_id", "date", "detail", "cost", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_date(self, obj):
        """ 🔹 날짜를 {year, month, day} 형식으로 변환 """
        return {"year": obj.date.year, "month": obj.date.month, "day": obj.date.day}

    def create(self, validated_data):
        store_id = validated_data.pop("store_id")
        category_id = validated_data.pop("category_id")

        store = get_object_or_404(Store, id=store_id)  # 🔹 존재하지 않으면 404 반환
        category = get_object_or_404(Category, id=category_id)  # 🔹 존재하지 않으면 404 반환

        # 🔹 날짜 정보 가져오기 & 예외 처리 추가
        date_data = self.context["request"].data.get("date", {})
        try:
            transaction_date = datetime(
                year=int(date_data.get("year", 0)), 
                month=int(date_data.get("month", 0)), 
                day=int(date_data.get("day", 0))
            )
        except ValueError:
            raise serializers.ValidationError("유효한 날짜 정보(year, month, day)가 필요합니다.")

        transaction = Transaction.objects.create(
            store=store,
            category=category,
            transaction_type=validated_data["transaction_type"],
            amount=validated_data["amount"],
            date=transaction_date,
            description=validated_data.get("description", ""),
        )

        return transaction
