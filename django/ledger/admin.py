from django.contrib import admin
from .models import Category  # ✅ Transaction 삭제

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # ✅ Admin 리스트에서 보이는 컬럼
    search_fields = ('name',)  # ✅ 검색 기능 추가
