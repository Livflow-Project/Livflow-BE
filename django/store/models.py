import uuid
from django.db import models
from users.models import CustomUser


# 가게 모델 정의
class Store(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)  # UUID 사용
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 가게 소유자
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)  # 선택적 필드
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return self.name
