import pandas as pd
from ledger.models import Transaction

def load_transaction_data():
    """
    거래 내역 데이터를 DataFrame으로 변환
    """
    transactions = Transaction.objects.all().values("date", "store__name", "category__name", "amount", "transaction_type")

    # Pandas DataFrame으로 변환
    df = pd.DataFrame(transactions)

    # 날짜 데이터를 DateTime 형식으로 변환
    df["date"] = pd.to_datetime(df["date"])

    # 연도, 월, 일 컬럼 추가
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df
