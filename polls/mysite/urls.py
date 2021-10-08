from django.contrib import admin
from django.urls import include, path

# django.urls.include将其他符合条件url的配置映射过来
urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]