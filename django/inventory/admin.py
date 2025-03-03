from django.contrib import admin
from .models import Inventory  # Inventory 모델 임포트

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "store", "remaining_stock", "unit")  # 관리자 페이지에서 보일 필드
    search_fields = ("ingredient__name", "store__name")  # 검색 필드 추가
    list_filter = ("store",)  # 필터링 기능 추가
