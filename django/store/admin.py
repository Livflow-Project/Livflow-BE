from django.contrib import admin
from .models import Category, Transaction, Store

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # ✅ 리스트에서 보이는 컬럼
    search_fields = ('name',)  # ✅ 검색 가능

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'address', 'created_at')  # ✅ 주요 정보 표시
    search_fields = ('name', 'user__email', 'address')  # ✅ 검색 가능
    list_filter = ('created_at',)  # ✅ 필터 추가
    raw_id_fields = ('user',)  # ✅ 사용자 선택을 편하게

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'store', 'transaction_type', 'amount', 'date', 'category')  # ✅ 주요 정보 표시
    search_fields = ('user__email', 'transaction_type', 'category__name', 'description')  # ✅ 검색 가능
    list_filter = ('transaction_type', 'date', 'category', 'store')  # ✅ 필터 추가
    raw_id_fields = ('user', 'category', 'store')  # ✅ ForeignKey 필드 편리하게 선택
