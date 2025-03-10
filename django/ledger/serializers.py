from rest_framework import serializers
from django.shortcuts import get_object_or_404
from store.models import Transaction, Store
from ledger.models import Category
from datetime import datetime
from rest_framework.exceptions import ValidationError

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class TransactionSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(write_only=True)  # 🔹 store_id 직접 받기
    category = serializers.CharField()  # 🔹 카테고리 이름을 직접 받음
    date = serializers.SerializerMethodField()
    cost = serializers.DecimalField(source="amount", max_digits=10, decimal_places=2)
    type = serializers.CharField(source="transaction_type")
    detail = serializers.CharField(source="description", required=False)  # 🔹 description -> detail

    class Meta:
        model = Transaction
        fields = ["id", "store_id", "type", "category", "date", "detail", "cost", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_date(self, obj):
        """ 🔹 날짜를 {year, month, day} 형식으로 변환 """
        return {"year": obj.date.year, "month": obj.date.month, "day": obj.date.day}

    def create(self, validated_data):
        store_id = validated_data.pop("store_id")
        category_name = validated_data.pop("category")  # 🔹 카테고리 이름 가져오기

        # 🔹 Store 찾기 (없으면 404 반환)
        store = get_object_or_404(Store, id=store_id)

        # 🔹 카테고리 찾기 (없으면 400 에러)
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            raise ValidationError({"category": f"'{category_name}' 카테고리가 존재하지 않습니다."})

        # 🔹 날짜 정보 확인
        date_data = self.context["request"].data.get("date", {})
        try:
            transaction_date = datetime(year=date_data["year"], month=date_data["month"], day=date_data["day"])
        except KeyError:
            raise ValidationError({"date": "날짜 정보(year, month, day)가 올바르지 않습니다."})

        # 🔹 거래 내역 생성
        transaction = Transaction.objects.create(
            store=store,
            category=category,
            transaction_type=validated_data["transaction_type"],
            amount=validated_data["amount"],
            date=transaction_date,
            description=validated_data.get("description", ""),
        )

        return transaction
