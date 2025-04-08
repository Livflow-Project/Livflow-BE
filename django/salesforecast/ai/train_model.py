# # Transaction → Pandas DataFrame으로 매출 데이터 불러오기

# # amount을 예측하는 TensorFlow 회귀 모델 학습

# # 학습에 사용된 카테고리 피처들 저장 (JSON)

# # 모델 저장 (.h5)


# import os
# import django
# import json
# import pandas as pd
# # import tensorflow as tf
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from salesforecast.ai.data_preprocessing import load_market_data


# # Django 설정
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livflow.settings')
# django.setup()

# from salesforecast.ai.data_preprocessing import load_sales_data

# # 🔹 학습 데이터 로드
# df = load_sales_data()

# # 🔹 카테고리 피처 저장용
# CATEGORICAL_FEATURES = {
#     "district": sorted(df["district"].unique().tolist()),
#     "menu": sorted(df["menu"].unique().tolist()),
#     "weekday": sorted(df["weekday"].unique().tolist()),
# }

# # 🔹 JSON으로 저장
# os.makedirs("salesforecast/ai/saved_model", exist_ok=True)
# with open("salesforecast/ai/saved_model/feature_categories.json", "w") as f:
#     json.dump(CATEGORICAL_FEATURES, f, ensure_ascii=False, indent=2)

# # 🔹 원-핫 인코딩
# df_encoded = pd.get_dummies(df, columns=["district", "menu", "weekday"])

# # 🔹 X, y 분리
# X = df_encoded.drop(columns=["amount"])
# y = df_encoded["amount"]

# # 🔹 정규화
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)


# # 🔹 Train/test 분리
# X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# # 🔹 모델 구성
# model = tf.keras.Sequential([
#     tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
#     tf.keras.layers.Dense(32, activation='relu'),
#     tf.keras.layers.Dense(1)  # 예측: 매출 금액
# ])

# model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# # 🔹 학습
# model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2)

# # 🔹 모델 저장
# model.save("salesforecast/ai/saved_model/sales_model.h5")
# print("✅ 모델 학습 및 저장 완료!")


# # salesforecast/ai/train_market_model.py

# df = load_market_data()

# # 🔹 카테고리 피처 저장
# categories = {
#     "district": sorted(df["district"].unique().tolist()),
#     "category": sorted(df["category"].unique().tolist())
# }
# os.makedirs("salesforecast/ai/saved_market_model", exist_ok=True)
# with open("salesforecast/ai/saved_market_model/market_features.json", "w") as f:
#     json.dump(categories, f, ensure_ascii=False)

# # 🔹 One-hot 인코딩
# df_encoded = pd.get_dummies(df, columns=["district", "category"])

# X = df_encoded.drop(columns=["amount"])
# y = df_encoded["amount"]

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# model = tf.keras.Sequential([
#     tf.keras.layers.Dense(64, activation='relu', input_shape=(X.shape[1],)),
#     tf.keras.layers.Dense(32, activation='relu'),
#     tf.keras.layers.Dense(1)
# ])
# model.compile(optimizer='adam', loss='mse')
# model.fit(X_train, y_train, epochs=100, batch_size=32)

# model.save("salesforecast/ai/saved_market_model/market_model.h5")
# print("✅ 상권 모델 학습 및 저장 완료!")
