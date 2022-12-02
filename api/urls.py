from django.urls import path
from api import views

urlpatterns = [
   # auth
  path('sign_up', views.SignUp.as_view(), name = 'signUpApi'),
  path('sign_in', views.SignIn.as_view(), name = 'signInApi'),

   # model views
  path('submit_self_report', views.InsertSelfReport.as_view(), name = 'submitSelfReportApi'),
  path('get_self_reports', views.GetSelfReports.as_view(), name = 'getSelfReportsApi'),
  path('submit_location', views.InsertLocation.as_view(), name = 'submitLocationApi'),
  path('submit_call_log', views.InsertCallLog.as_view(), name = 'submitCallLogApi'),
  path('submit_activity_transition', views.InsertActivityTransition.as_view(), name = 'submitActivityTransitionApi'),
  path('submit_activity_recognition', views.InsertActivityRecognition.as_view(), name = 'submitActivityRecognitionApi'),
  path('submit_screen_state', views.InsertScreenState.as_view(), name = 'submitScreenStateApi'),
  path('submit_calendar_event', views.InsertCalendarEvent.as_view(), name = 'submitCalendarEventApi'),

   # custom views
  path('set_fcm_token', views.SetFcmToken.as_view(), name = 'setFcmTokenApi'),

   # file views
  path('submit_ppg', views.InsertPPG.as_view(), name = 'submitPPGApi'),
  path('submit_acc', views.InsertAcc.as_view(), name = 'submitAccApi'),
  path('submit_off_body', views.InsertOffBody.as_view(), name = 'submitOffBodyApi'),

   # push notification view
  path('send_ema_push', views.SendEmaPush.as_view(), name = 'sendEMAPushApi'),
]
