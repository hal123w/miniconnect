from django.contrib import admin
from django.urls import path, include
from django.conf import settings # 追加
from django.conf.urls.static import static # 追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sns.urls')),
    path('', include('django.contrib.auth.urls')),
]

# 開発環境で画像を表示するための設定を追加
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)