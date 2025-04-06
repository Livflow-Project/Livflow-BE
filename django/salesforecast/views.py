# salesforecast/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from salesforecast.ai.predict import predict_sales
from salesforecast.ai.predict import predict_market_sales


class SalesPredictAPIView(APIView):
    def post(self, request):
        district = request.data.get("district")
        menu = request.data.get("menu")
        date = request.data.get("date")  # yyyy-mm-dd

        if not all([district, menu, date]):
            return Response({"error": "district, menu, date는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            predicted = predict_sales(district, menu, date)
            return Response({"predicted_sales": int(predicted)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarketForecastAPIView(APIView):
    def get(self, request):
        district = request.GET.get("district")
        category = request.GET.get("category")
        year = request.GET.get("year")
        month = request.GET.get("month")

        if not all([district, category, year, month]):
            return Response({"error": "district, category, year, month는 필수입니다."}, status=400)

        try:
            year = int(year)
            month = int(month)
            predicted = predict_market_sales(district, category, year, month)
            return Response({"predicted_sales": int(predicted)}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)