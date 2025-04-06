# salesforecast/ai/predict.py

import os
import json
import pandas as pd
import tensorflow as tf
from datetime import datetime

# 경로 상수
MODEL_PATH = "salesforecast/ai/saved_model/sales_model.h5"
CATEGORY_PATH = "salesforecast/ai/saved_model/feature_categories.json"

# 매출 분석 함수
def predict_sales(district: str, menu: str, date_str: str) -> float:
    # 🔹 날짜 파싱
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("날짜 형식은 'YYYY-MM-DD'여야 합니다.")
    
    month = date_obj.month
    weekday = date_obj.strftime("%A")  # Monday ~ Sunday

    # 🔹 범주 피처 불러오기
    if not os.path.exists(CATEGORY_PATH):
        raise FileNotFoundError("❌ feature_categories.json이 없습니다. train_model.py 먼저 실행하세요.")

    with open(CATEGORY_PATH, "r") as f:
        categories = json.load(f)

    # 🔹 입력값을 기반으로 원-핫 벡터 생성
    input_dict = {"month": month}

    for d in categories["district"]:
        input_dict[f"district_{d}"] = 1 if d == district else 0

    for m in categories["menu"]:
        input_dict[f"menu_{m}"] = 1 if m == menu else 0

    for w in categories["weekday"]:
        input_dict[f"weekday_{w}"] = 1 if w == weekday else 0

    input_df = pd.DataFrame([input_dict])

    # 🔹 모델 불러오기
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("❌ sales_model.h5가 없습니다. train_model.py 먼저 실행하세요.")
    
    model = tf.keras.models.load_model(MODEL_PATH)

    # 🔹 예측
    prediction = model.predict(input_df)
    return float(prediction[0][0])


#상권분석 함수
def predict_market_sales(district: str, category: str, year: int, month: int) -> float:
    with open("salesforecast/ai/saved_market_model/market_features.json", "r") as f:
        features = json.load(f)

    input_data = {"year": year, "month": month}
    for d in features["district"]:
        input_data[f"district_{d}"] = 1 if d == district else 0
    for c in features["category"]:
        input_data[f"category_{c}"] = 1 if c == category else 0

    df_input = pd.DataFrame([input_data])
    model = tf.keras.models.load_model("salesforecast/ai/saved_market_model/market_model.h5")
    pred = model.predict(df_input)
    return float(pred[0][0])
