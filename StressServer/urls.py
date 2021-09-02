from django.contrib import admin
from django.urls import path
from django.urls import include
from StressServer import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('api/', include('api.urls')),

    path('', views.handle_index, name='index'),
]
