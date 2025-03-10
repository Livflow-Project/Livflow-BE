from rest_framework import serializers
from django.shortcuts import get_object_or_404
from store.models import Transaction, Store, Category
from datetime import datetime
from rest_framework.exceptions import ValidationError

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class TransactionSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(write_only=True)
    category = serializers.CharField()  # 🔹 카테고리 이름을 직접 받음
    date = serializers.SerializerMethodField()
    cost = serializers.DecimalField(source="amount", max_digits=10, decimal_places=2)
    type = serializers.CharField(source="transaction_type")
    detail = serializers.CharField(source="description", required=False)

    class Meta:
        model = Transaction
        fields = ["id", "store_id", "type", "category", "date", "detail", "cost", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_date(self, obj):
        return {"year": obj.date.year, "month": obj.date.month, "day": obj.date.day}

    def create(self, validated_data):
        store_id = validated_data.pop("store_id")
        category_name = validated_data.pop("category")

        store = get_object_or_404(Store, id=store_id)

        # ✅ 카테고리 찾기 (없으면 생성)
        category, created = Category.objects.get_or_create(name=category_name)

        date_data = self.context["request"].data.get("date", {})
        transaction_date = datetime(year=date_data["year"], month=date_data["month"], day=date_data["day"])

        # ✅ `request.user`를 사용해 현재 로그인한 사용자 자동 저장
        transaction = Transaction.objects.create(
            user=self.context["request"].user,  # 🔥 로그인한 사용자 자동 저장
            store=store,
            category=category,
            transaction_type=validated_data["transaction_type"],
            amount=validated_data["amount"],
            date=transaction_date,
            description=validated_data.get("description", ""),
        )

        return transaction

