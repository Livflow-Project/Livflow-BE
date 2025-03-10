from django.contrib import admin
from ledger.models import Category as LedgerCategory, Transaction  # ✅ 가계부 카테고리

@admin.register(LedgerCategory)
class LedgerCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # ✅ 가계부 항목명
    search_fields = ('name',)  # ✅ 검색 가능

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'store', 'transaction_type', 'amount', 'date', 'category')
    search_fields = ('user__email', 'transaction_type', 'category__name', 'description')
    list_filter = ('transaction_type', 'date', 'category', 'store')
    raw_id_fields = ('user', 'category', 'store')
