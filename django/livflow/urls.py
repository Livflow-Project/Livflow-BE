from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # 'users' 앱의 URL 패턴에 'api/users/' 경로 추가
]
