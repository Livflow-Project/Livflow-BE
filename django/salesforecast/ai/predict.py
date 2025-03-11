import numpy as np
from .train_model import build_sales_model

def predict_sales(future_date):
    """미래 특정 날짜의 매출 예측"""
    model, X, y = build_sales_model()

    # 데이터 준비 (날짜를 숫자로 변환)
    future_timestamp = pd.to_datetime(future_date).timestamp()
    future_data = np.array([[future_timestamp, 0]])  # amount는 더미 값

    # 모델 예측
    prediction = model.predict(future_data)
    return prediction[0][0]  # 예측된 매출 값 반환
