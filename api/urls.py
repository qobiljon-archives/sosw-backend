from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('login', views.handle_login_api),
    path('register', views.handle_register_api),
    path('submit_data', views.handle_submit_data_api),
]
