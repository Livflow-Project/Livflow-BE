from django.db import models
from users.models import CustomUser  # CustomUser 모델과 연결

# 카테고리 모델 정의 (Transaction에서 사용)
class Category(models.Model):
    name = models.CharField(max_length=100)  # 카테고리 이름

    def __str__(self):
        return self.name

# 가계부 거래 내역 모델
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    # related_name을 'store_transactions'로 변경하여 충돌 해결
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_transactions')  # 사용자와 연결
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 금액
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)  # 수입 또는 지출 구분
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # 카테고리와 연결
    date = models.DateField()  # 거래 발생 날짜
    description = models.TextField(blank=True, null=True)  # 설명 (선택 사항)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.user.email}'s {self.transaction_type} on {self.date} for {self.amount}"

    @classmethod
    def get_totals(cls, user):
        # 수입과 지출을 계산하는 메서드 (유저별)
        income_total = cls.objects.filter(user=user, transaction_type='income').aggregate(total=models.Sum('amount'))['total'] or 0
        expense_total = cls.objects.filter(user=user, transaction_type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
        balance = income_total - expense_total
        return {
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': balance
        }

# 가게 모델 정의
class Store(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 사용자와 연결
    name = models.CharField(max_length=100)  # 가게 이름
    address = models.CharField(max_length=255)  # 가게 주소
    created_at = models.DateTimeField(auto_now_add=True)  # 가게 등록 시간

    def __str__(self):
        return self.name

    # 가계부 내역의 카테고리별 수입/지출 총합 계산
    def get_ledger_summary(self):
        income = Transaction.objects.filter(user=self.user, transaction_type='income').values('category__name').annotate(total_income=models.Sum('amount'))
        expense = Transaction.objects.filter(user=self.user, transaction_type='expense').values('category__name').annotate(total_expense=models.Sum('amount'))

        return {
            'income': {item['category__name']: item['total_income'] for item in income},
            'expense': {item['category__name']: item['total_expense'] for item in expense}
        }
