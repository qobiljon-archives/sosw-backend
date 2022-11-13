from django.urls import path
from api import views

urlpatterns = [
   # auth
  path('sign_up', views.SignUp.as_view(), name = 'signUpApi'),
  path('sign_in', views.SignIn.as_view(), name = 'signInApi'),
  path('submit_self_report', views.InsertSelfReport.as_view(), name = 'submitSelfReportApi'),
  path('submit_bvp', views.InsertBVP.as_view(), name = 'submitBVPApi'),

   # path('submit_acc', views.handle_submit_accelerometer_data_api, name = 'submit_acc_data'),
   # path('submit_off_body', views.handle_submit_off_body_api, name = 'submit_off_body_api'),
   # path('send_ema_push', views.handle_send_ema_push_api, name = 'send_ema_push_api'),
]
