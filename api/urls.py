from django.urls import path
from api import views

urlpatterns = [
	path('login', views.handle_login_api, name='login_api'),
	path('register', views.handle_register_api, name='register_api'),
	path('set_fcm_token', views.handle_set_fcm_token_api, name='set_fcm_token_api'),
	path('send_ema_notification', views.handle_send_ema_notification_api, name='send_ema_notification_api'),
	path('submit_bvp_data', views.handle_submit_bvp_data_api, name='submit_bvp_data'),
	path('submit_acc_data', views.handle_submit_accelerometer_data_api, name='submit_acc_data'),
	path('submit_ema', views.handle_submit_ema_api, name='submit_ema_api'),
]
