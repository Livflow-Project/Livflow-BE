from django.db import models
from users.models import CustomUser  # CustomUser 모델과 연결

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 사용자와 연결 (소셜 로그인 이메일 사용)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 금액, 기본값 0
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)  # 수입 또는 지출
    category = models.CharField(max_length=100, blank=True, null=True)  # 카테고리 (선택 사항)
    date = models.DateField()  # 거래 발생 날짜
    description = models.TextField(blank=True, null=True)  # 설명 (선택 사항)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.user.email}'s {self.transaction_type} on {self.date} for {self.amount}"

    # 지출/수입 구분
    @property
    def is_expense(self):
        return self.transaction_type == 'expense'

    @property
    def is_income(self):
        return self.transaction_type == 'income'

    # 수입/지출/잔액 총합 계산 (유저별)
    @classmethod
    def get_totals(cls, user):
        income_total = cls.objects.filter(user=user, transaction_type='income').aggregate(total=models.Sum('amount'))['total'] or 0
        expense_total = cls.objects.filter(user=user, transaction_type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
        balance = income_total - expense_total
        return {
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': balance
        }
