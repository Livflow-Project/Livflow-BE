from rest_framework import serializers
from .models import Category, Transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']  # 모든 필드 포함

class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # `Category` 정보 포함 (읽기 전용)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',  # 내부적으로 연결될 모델 필드
        write_only=True     # 입력 전용 필드
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 'category', 'category_id', 'transaction_type', 'amount', 'remarks', 'user_id'
        ]
        read_only_fields = ['id', 'user_id']  # ID와 사용자 ID는 읽기 전용
