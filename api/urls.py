from django.urls import path
from api import views

urlpatterns = [
	path('auth', views.handle_auth_api, name='auth_api'),

	path('send_ema_push', views.handle_send_ema_push_api, name='send_ema_push_api'),

	path('set_fcm_token', views.handle_set_fcm_token_api, name='set_fcm_token_api'),

	path('submit_bvp', views.handle_submit_bvp_data_api, name='submit_bvp_data'),
	path('submit_acc', views.handle_submit_accelerometer_data_api, name='submit_acc_data'),
	path('submit_ema', views.handle_submit_ema_api, name='submit_ema_api'),
]
