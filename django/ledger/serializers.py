from rest_framework import serializers
from django.shortcuts import get_object_or_404
from store.models import Store
from ledger.models import Transaction, Category
from datetime import datetime
from rest_framework.exceptions import ValidationError


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class TransactionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.UUIDField(source="id", read_only=True)  # ✅ `id` → `transaction_id` 변경
    store_id = serializers.UUIDField(write_only=True)  # ✅ 요청 시 필요하지만 응답에는 포함하지 않음
    category = serializers.CharField()  # ✅ 카테고리 이름 직접 받음
    cost = serializers.DecimalField(
        source="amount", max_digits=10, decimal_places=2, coerce_to_string=False
    )  # ✅ Decimal → float 변환
    type = serializers.CharField(source="transaction_type")  # ✅ "transaction_type" → "type"
    detail = serializers.CharField(source="description", required=False)  # ✅ "description" → "detail"

    class Meta:
        model = Transaction
        fields = ["transaction_id", "store_id", "type", "category", "detail", "cost"]  # ✅ "date" 제거
        read_only_fields = ["transaction_id"]
        
    def validate_category(self, value):
        if isinstance(value, Category):  
            return value  # ✅ 이미 Category 객체라면 그대로 반환

        if isinstance(value, int) or str(value).isdigit():  
            return get_object_or_404(Category, id=int(value))  # ✅ ID로 변환

        category, _ = Category.objects.get_or_create(name=value)  # ✅ 이름으로 변환
        return category  

    def create(self, validated_data):
        store_id = validated_data.pop("store_id")
        category_name = validated_data.pop("category")

        store = get_object_or_404(Store, id=store_id)
        category = self.validate_category(category_name)  # ✅ ForeignKey 변환

        date_data = self.context["request"].data.get("date", {})
        try:
            transaction_date = datetime(
                year=date_data["year"], month=date_data["month"], day=date_data["day"]
            ).date()  # ✅ `datetime` → `date` 변환
        except KeyError:
            raise ValidationError({"date": "year, month, day 값을 포함해야 합니다."})

        # ✅ `request.user`를 사용해 현재 로그인한 사용자 자동 저장
        transaction = Transaction.objects.create(
            user=self.context["request"].user,
            store=store,
            category=category,
            transaction_type=validated_data["transaction_type"],
            amount=validated_data["amount"],
            date=transaction_date,
            description=validated_data.get("description", ""),
        )

        return transaction
    def update(self, instance, validated_data):

        if "category" in validated_data:
            instance.category = self.validate_category(validated_data.pop("category"))  # ✅ ForeignKey 변환 후 저장
        return super().update(instance, validated_data)
