# import numpy as np
# import tensorflow as tf
# import pandas as pd
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from salesforecast.ai.data_preprocessing import load_transaction_data

# class SalesForecastView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """
#         특정 카테고리(업종)와 날짜를 입력하면 매출을 예측하는 API
#         """
#         category = request.GET.get("category")  # 예: '카페'
#         year = int(request.GET.get("year", 2025))
#         month = int(request.GET.get("month", 6))

#         if not category:
#             return Response({"error": "카테고리(category)를 입력해주세요."}, status=400)

#         # 1️⃣ 저장된 모델 불러오기
#         model = tf.keras.models.load_model("sales_forecast_model.h5")

#         # 2️⃣ 데이터 로드 및 전처리
#         df = load_transaction_data()
#         df = df[["year", "month", "category__name"]]
#         df = pd.get_dummies(df, columns=["category__name"])

#         # 3️⃣ 입력 데이터 만들기
#         input_data = pd.DataFrame({"year": [year], "month": [month], "category__name_" + category: [1]})
#         input_data = input_data.reindex(columns=df.columns, fill_value=0)

#         # 4️⃣ 예측 수행
#         prediction = model.predict(input_data)
#         predicted_sales = float(prediction[0][0])  # 예측 결과 변환

#         return Response({
#             "category": category,
#             "year": year,
#             "month": month,
#             "predicted_sales": predicted_sales
#         }, status=200)
