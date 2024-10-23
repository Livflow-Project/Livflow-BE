from django.db import models
from users.models import CustomUser  # CustomUser 모델과 연결

# 카테고리 모델 정의
# 카테고리 항목은 id 숫자로 장고 admin에 직접 추가해서 숫자로만 들고옴
class Category(models.Model):
    name = models.CharField(max_length=100)  # 카테고리 이름

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    # related_name을 'ledger_transactions'로 설정하여 store 모델과 구분
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ledger_transactions')  # 사용자와 연결 (소셜 로그인 이메일 사용)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 금액, 기본값 0
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)  # 수입 또는 지출
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # 카테고리와 연결
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
