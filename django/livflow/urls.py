from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # 'users' 앱의 URL 패턴
    path('api/stores/', include('store.urls')),  # 'store' 앱의 URL 패턴 추가
    path('api/costcalcul/', include('costcalcul.urls')),  # 'costcalcul' 앱의 URL 패턴 추가
    path('api/ledger/', include('ledger.urls')),  # 'ledger' 앱의 URL 패턴 추가
]
