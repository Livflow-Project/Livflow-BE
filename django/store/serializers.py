from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(source='id', read_only=True)

    class Meta:
        model = Store
        fields = ['store_id', 'name', 'address']
