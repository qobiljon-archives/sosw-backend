from django.urls import path
from api import views

urlpatterns = [
    path('/', views.handle_login_api),
    path('login', views.handle_login_api),
    path('register', views.handle_register_api),
    path('submit_data', views.handle_submit_data_api),
    path('submit_ema', views.handle_submit_ema_api),
]
