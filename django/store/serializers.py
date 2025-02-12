from rest_framework import serializers
from .models import Store, Transaction, Category

class StoreSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(source='id', read_only=True)

    class Meta:
        model = Store
        fields = ['store_id', 'name', 'address']

class TransactionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.UUIDField(source='id', read_only=True)

    class Meta:
        model = Transaction
        fields = ['transaction_id', 'transaction_type', 'category', 'description', 'amount', 'date']
