from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'user', 'name', 'address']
        read_only_fields = ['id', 'user']
