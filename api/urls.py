from django.urls import path
from api import views

urlpatterns = [
   # auth
  path('sign_up', views.SignUp.as_view(), name = 'signUpApi'),
  path('sign_in', views.SignIn.as_view(), name = 'signInApi'),
  path('submit_self_report', views.InsertSelfReport.as_view(), name = 'submitSelfReportApi'),
  path('submit_ppg', views.InsertPPG.as_view(), name = 'submitPPGApi'),
  path('submit_acc', views.InsertAcc.as_view(), name = 'submitAccApi'),
  path('submit_off_body', views.InsertOffBody.as_view(), name = 'submitOffBodyApi'),
   #   path('send_ema_push', views.handle_send_ema_push_api, name = 'sendEMAPushApi'),
]
