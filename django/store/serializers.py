from rest_framework import serializers
from .models import Store
from rest_framework.response import Response
from rest_framework import status

# store.serializers.py
class StoreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(help_text="가게의 이름을 입력하세요.")
    address = serializers.CharField(help_text="가게의 주소를 입력하세요.")
    
    class Meta:
        model = Store
        fields = ['id', 'user', 'name', 'address']
        read_only_fields = ['id']

# views.py - StoreListView 클래스의 post 메소드 수정
def post(self, request):
    store_data = {
        "name": request.data.get("name"),
        "address": request.data.get("address"),
        "user": request.user.id  # 사용자 정보를 명시적으로 store_data에 추가합니다.
    }
    serializer = StoreSerializer(data=store_data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
