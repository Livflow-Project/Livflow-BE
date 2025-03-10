from django.contrib import admin
from store.models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "category", "transaction_type", "amount", "date"]
    list_filter = ["transaction_type", "store"]
    search_fields = ["category__name", "store__name"]
