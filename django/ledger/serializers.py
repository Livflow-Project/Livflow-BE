from rest_framework import serializers
from .models import Transaction, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TransactionSerializer(serializers.ModelSerializer):
    # 카테고리의 세부 정보를 포함하여 직렬화
    category = CategorySerializer(read_only=True)  # 읽기 전용
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',  # 내부 필드에 연결
        write_only=True     # 쓰기 전용
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'amount', 'transaction_type',
            'category', 'category_id', 'date', 'description',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']  # 일부 필드 읽기 전용
