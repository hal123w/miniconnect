from django.contrib import admin
from django.urls import path, include # include だけでOK

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sns.urls')), # ここはそのまま
    path('accounts/', include('django.contrib.auth.urls')),
]
