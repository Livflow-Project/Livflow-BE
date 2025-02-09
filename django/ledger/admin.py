from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # ✅ Admin 리스트에서 보이는 컬럼
    search_fields = ('name',)  # ✅ 검색 기능 추가

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction_type', 'amount', 'date', 'category')  # ✅ 주요 정보 표시
    search_fields = ('user__email', 'transaction_type', 'category__name', 'description')  # ✅ 검색 가능
    list_filter = ('transaction_type', 'date', 'category')  # ✅ 필터 추가
    raw_id_fields = ('user', 'category')  # ✅ ForeignKey 필드 편리하게 선택
