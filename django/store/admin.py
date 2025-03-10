from django.contrib import admin
from store.models import Store, Category as StoreCategory  # ✅ 업종 카테고리

@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # ✅ 업종명
    search_fields = ('name',)  # ✅ 검색 가능

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'address', 'created_at')
    search_fields = ('name', 'user__email', 'address')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)
