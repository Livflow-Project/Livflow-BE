from django.contrib import admin
from .models import Store, Transaction

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'created_at')  # ✅ 가게 정보 표시
    search_fields = ('name', 'user__email')  # ✅ 가게 이름, 유저 이메일 검색 가능
    list_filter = ('created_at',)  # ✅ 생성 날짜 필터 추가

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'user', 'transaction_type', 'amount', 'date', 'category')  # ✅ 주요 정보 표시
    search_fields = ('user__email', 'store__name', 'transaction_type', 'category__name', 'description')  # ✅ 검색 가능
    list_filter = ('transaction_type', 'date', 'category', 'store')  # ✅ 필터 추가
    raw_id_fields = ('user', 'category', 'store')  # ✅ ForeignKey 필드 편리하게 선택
