from django.contrib import admin
from django.urls import path
from django.urls import include
from dashboard import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
  path('admin/', admin.site.urls, name = 'admin'),
  path('', views.handle_index, name = 'index'),
  path('api/', include('api.urls')),
  path('api-auth/', include('rest_framework.urls')),
]
urlpatterns += staticfiles_urlpatterns()
