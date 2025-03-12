import uuid
from django.db import models
from users.models import CustomUser
from django.utils.timezone import now
from store.models import Store 


# ✅ 1️⃣ 가계부 카테고리 (ledger category)
class Category(models.Model):  
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_category(cls):
        """ ✅ 기본 '미분류' 카테고리 가져오기 (없으면 생성) """
        category, created = cls.objects.get_or_create(name="미분류")
        return category.id


# ✅ 2️⃣ 가계부 거래 내역 모델
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ledger_transactions")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="ledger_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)

    # 🔥 ForeignKey 기본값을 '미분류'로 설정
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=Category.get_default_category,
        related_name="ledger_transactions"  # ✅ store.Transaction과 구분
    )

    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ledger_transaction"  # ✅ 테이블을 ledger_transaction으로 변경

    def __str__(self):
        return f"{self.user.email}'s {self.transaction_type} on {self.date} for {self.amount}"

