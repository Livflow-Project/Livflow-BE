from rest_framework import serializers
from store.models import Transaction
from ledger.models import Category
from store.models import Store
from datetime import datetime

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TransactionSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(write_only=True)  # 🔹 store_id 직접 받기
    category = serializers.CharField(source='category.name', read_only=True)  # 🔹 카테고리 이름만 반환
    category_id = serializers.CharField(write_only=True)  # 🔹 카테고리 ID는 요청 시 사용
    date = serializers.SerializerMethodField()
    cost = serializers.DecimalField(source="amount", max_digits=10, decimal_places=2)
    type = serializers.CharField(source="transaction_type")

    class Meta:
        model = Transaction
        fields = ['id', 'store_id', 'type', 'category', 'category_id', 'date', 'detail', 'cost', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_date(self, obj):
        """ 🔹 날짜를 {year, month, day} 형식으로 변환 """
        return {"year": obj.date.year, "month": obj.date.month, "day": obj.date.day}

    def create(self, validated_data):
        store_id = validated_data.pop("store_id")
        category_id = validated_data.pop("category_id")
        
        store = Store.objects.get(id=store_id)  # 🔹 store_id 직접 매칭
        category = Category.objects.get(id=category_id)  # 🔹 category_id 직접 매칭

        date_data = self.context["request"].data.get("date", {})
        transaction_date = datetime(year=date_data["year"], month=date_data["month"], day=date_data["day"])

        transaction = Transaction.objects.create(
            store=store,
            category=category,
            transaction_type=validated_data["transaction_type"],
            amount=validated_data["amount"],
            date=transaction_date,
            description=validated_data.get("description", ""),
        )

        return transaction
