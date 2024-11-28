from rest_framework import serializers
from .models import Store



class StoreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(help_text="가게의 이름을 입력하세요.")
    address = serializers.CharField(help_text="가게의 주소를 입력하세요.")
    
    class Meta:
        model = Store
        fields = ['id', 'user', 'name', 'address']
        read_only_fields = ['id', 'user']
