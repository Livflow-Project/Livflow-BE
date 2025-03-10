import uuid
from django.db import models
from users.models import CustomUser
from django.utils.timezone import now


# 카테고리 모델 정의
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 중복 방지

    def __str__(self):
        return self.name

# 가계부 거래 내역 모델
class Transaction(models.Model):
    
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)  # UUID 사용
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_transactions')  # 사용자와 연결
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='transactions', default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 금액
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)  # 수입 또는 지출 구분
    category = models.ForeignKey("ledger.Category", on_delete=models.SET_NULL, null=True, blank=True) 
    date = models.DateField()  # 거래 발생 날짜
    description = models.TextField(blank=True, null=True)  # 설명 (선택 사항)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.user.email}'s {self.transaction_type} on {self.date} for {self.amount}"

    @classmethod
    def get_totals(cls, user, store=None):
        """
        해당 사용자의 전체 수입과 지출을 집계.
        특정 가게(store)를 지정하면 해당 가게의 총합 반환.
        """
        filters = {'user': user}
        if store:
            filters['store'] = store

        income_total = cls.objects.filter(**filters, transaction_type='income').aggregate(total=models.Sum('amount'))['total'] or 0
        expense_total = cls.objects.filter(**filters, transaction_type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
        balance = income_total - expense_total

        return {
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': balance
        }

    @classmethod
    def get_current_month_totals(cls, user, store):
        """
        현재 월의 카테고리별 거래 합산
        """
        today = now()
        transactions = cls.objects.filter(
            user=user, store=store,
            date__year=today.year, date__month=today.month
        ).values('transaction_type', 'category__name').annotate(total=models.Sum('amount'))

        return [
            {"type": t["transaction_type"], "category": t["category__name"], "cost": t["total"]}
            for t in transactions
        ]

# 가게 모델 정의
class Store(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)  # UUID 사용
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 가게 소유자
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)  # 선택적 필드
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return self.name

    def get_ledger_summary(self):
        """
        해당 가게의 카테고리별 수입/지출 총합을 계산
        """
        income = Transaction.objects.filter(
            user=self.user, store=self, transaction_type='income'
        ).values('category__name').annotate(total_income=models.Sum('amount'))

        expense = Transaction.objects.filter(
            user=self.user, store=self, transaction_type='expense'
        ).values('category__name').annotate(total_expense=models.Sum('amount'))

        return {
            'income': {item['category__name']: item['total_income'] for item in income},
            'expense': {item['category__name']: item['total_expense'] for item in expense}
        }
