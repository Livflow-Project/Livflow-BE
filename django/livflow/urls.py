from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger 설정
schema_view = get_schema_view(
   openapi.Info(
      title="Livflow API",
      default_version='v1',
      description="Livflow 가계부, 단가계산기 api 입니다.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="dudrknd1642@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# URL 패턴
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # 'users' 앱의 URL 패턴
    path('api/stores/', include('store.urls')),  # 'store' 앱의 URL 패턴 추가
    path('api/costcalcul/', include('costcalcul.urls')),  # 'costcalcul' 앱의 URL 패턴 추가
    path('api/ledger/', include('ledger.urls')),  # 'ledger' 앱의 URL 패턴 추가
    
    # Swagger 및 Redoc 경로 추가
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # JSON 경로 추가
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
