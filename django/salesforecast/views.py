import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


FASTAPI_BASE_URL = "http://172.30.1.65:8000"  # 로컬 FastAPI 서버 주소로 바꿔줘

class SalesPredictAPIView(APIView):
    def post(self, request):
        district = request.data.get("district")
        menu = request.data.get("menu")
        date = request.data.get("date")  # yyyy-mm-dd

        if not all([district, menu, date]):
            return Response({"error": "district, menu, date는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.post(
                f"{FASTAPI_BASE_URL}/predict",
                json={"district": district, "menu": menu, "date_str": date},
                timeout=5
            )
            if response.status_code == 200:
                return Response(response.json(), status=200)
            return Response({"error": "FastAPI 서버 오류", "detail": response.text}, status=500)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class MarketForecastAPIView(APIView):
    def get(self, request):
        district = request.GET.get("district")
        category = request.GET.get("category")
        year = request.GET.get("year")
        month = request.GET.get("month")

        if not all([district, category, year, month]):
            return Response({"error": "district, category, year, month는 필수입니다."}, status=400)

        try:
            response = requests.post(
                f"{FASTAPI_BASE_URL}/market-predict",
                json={
                    "district": district,
                    "category": category,
                    "year": int(year),
                    "month": int(month)
                },
                timeout=5
            )
            if response.status_code == 200:
                return Response(response.json(), status=200)
            return Response({"error": "FastAPI 서버 오류", "detail": response.text}, status=500)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
