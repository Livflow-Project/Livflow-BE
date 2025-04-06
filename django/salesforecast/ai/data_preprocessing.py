# 모델 학습/예측에 사용할 데이터를 전처리해주는 핵심 함수들을 담는 파일

# salesforecast/ai/data_preprocessing.py

import pandas as pd
from ledger.models import Transaction
from datetime import datetime

def load_sales_data():
    """ Transaction 모델에서 income만 불러와 학습용 데이터프레임 생성 """
    qs = Transaction.objects.filter(transaction_type='income').select_related('store', 'category')

    records = []
    for t in qs:
        # 예: "서울 강남구 테헤란로 1" → "강남구"
        try:
            district = t.store.address.split()[1]
        except Exception:
            district = "unknown"

        records.append({
            "date": t.date,
            "district": district,
            "menu": t.category.name if t.category else "기타",
            "amount": float(t.amount),
        })

    df = pd.DataFrame(records)

    # 날짜 기반 피처 추가
    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.day_name()

    # 필요없는 컬럼 제거
    df.drop(columns=["date"], inplace=True)

    return df
