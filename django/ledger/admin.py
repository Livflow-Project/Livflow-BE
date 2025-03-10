from django.contrib import admin
from .models import Category  # ✅ Transaction 삭제
from store.models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "category", "transaction_type", "amount", "date"]
    list_filter = ["transaction_type", "store"]
    search_fields = ["category__name", "store__name"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # ✅ Admin 리스트에서 보이는 컬럼
    search_fields = ('name',)  # ✅ 검색 기능 추가
