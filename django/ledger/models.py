from django.db import models

# 카테고리 모델 정의
# 카테고리 항목은 id 숫자로 장고 admin에 직접 추가해서 숫자로만 들고옴
class Category(models.Model):
    name = models.CharField(max_length=100)  # 카테고리 이름

    def __str__(self):
        return self.name
