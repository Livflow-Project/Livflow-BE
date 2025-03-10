from django.contrib import admin
from .models import Category  # ✅ Transaction 삭제

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "category", "transaction_type", "amount", "date"]
    list_filter = ["transaction_type", "store"]
    search_fields = ["category__name", "store__name"]
