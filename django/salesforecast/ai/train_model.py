# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense, LSTM
# import numpy as np
# from .data_preprocessing import load_sales_data

# def build_sales_model():
#     """매출 예측을 위한 LSTM 모델 생성"""
#     df = load_sales_data()

#     # 데이터 전처리 (예: 날짜를 숫자로 변환)
#     df["timestamp"] = df["date"].astype(int) // 10**9

#     X = df[["timestamp", "amount"]].values  # 입력 데이터
#     y = df["amount"].values  # 예측할 값

#     # LSTM 모델 생성
#     model = Sequential([
#         LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
#         LSTM(50, return_sequences=False),
#         Dense(25, activation="relu"),
#         Dense(1)
#     ])

#     model.compile(optimizer="adam", loss="mse")

#     return model, X, y
