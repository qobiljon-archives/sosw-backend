import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")
django.setup()

import firebase_admin
from firebase_admin import messaging
from firebase_admin import exceptions
from random import randint
import threading
import time
from datetime import datetime
from datetime import timedelta
from requests.exceptions import HTTPError
from typing import List

from api import models as mdl
from api.views import firebase_app
from api import services as svc

NOTIFICATIONS_PER_DAY = 12
NOTIFICATION_HOUR_RANGE = {'from': 9, 'till': 21}
NOTIFICATION_DELAY_RANGE = {'min': 40, 'max': 80}

# Firebase sdk
if not firebase_admin._apps:
  cred = firebase_admin.credentials.Certificate('fcm_secret.json')
  firebase_app = firebase_admin.initialize_app(credential = cred)


def get_daily_notification_timings() -> List[datetime]:
  ans: List[datetime] = list()

  dt = datetime.now()
  if dt.hour <= NOTIFICATION_HOUR_RANGE['from']:
    dt = dt.replace(hour = max(dt.hour, NOTIFICATION_HOUR_RANGE['from']), minute = 0, second = 0, microsecond = 0)

  while dt.hour < NOTIFICATION_HOUR_RANGE['till'] and len(ans) < NOTIFICATIONS_PER_DAY:
    delta = timedelta(minutes = randint(NOTIFICATION_DELAY_RANGE['min'], NOTIFICATION_DELAY_RANGE['max']))
    ans.append(dt)
    dt += delta

  return ans


def send_push_notification(user: mdl.User) -> bool:
  try:
    messaging.send(
      message = messaging.Message(
        android = messaging.AndroidConfig(
          priority = 'high',
          notification = messaging.AndroidNotification(
            title = "Stress report time!",
            body = "Please log your current situation and stress levels.",
            channel_id = 'sosw.app.push',
          ),
        ),
        token = user.fcm_token,
      ),
      app = firebase_app,
    )
    svc.create_self_report_log(timestamp = int(time.time()*1000), user = user, voluntary = False)
    return True
  except messaging.UnregisteredError:
    user.fcm_token = None
    user.save()
    return False
  except exceptions.UnavailableError:
    print('FCM service is temporarily unavailable')
    user.fcm_token = None
    user.save()
    return False
  except exceptions.FirebaseError:
    user.fcm_token = None
    user.save()
    return False


def init():
  day = datetime.now().day
  threads = set()

  while True:
    for user in mdl.User.objects.exclude(fcm_token__isnull = True):
      if user not in threads and user.fcm_token:
        timings = get_daily_notification_timings()

        for dt in timings:
          threading.Timer(
            interval = (dt - datetime.now()).total_seconds(),
            function = send_push_notification,
            args = [user],
          ).start()

        if len(timings) == 1:
          print(f'EMA for participant({user.full_name}): {timings[0].strftime("%m/%d %H:%M")}')
        elif len(timings) > 1:
          print(
            f'EMA for participant({user.id}): {timings[0].strftime("%m/%d %H:%M")}',
            ", ".join([x.strftime("%H:%M") for x in timings[1:]]),
          )
        threads.add(user)

    time.sleep(20*60)
    if day != datetime.now().day:
      day = datetime.now().day
      threads.clear()


if __name__ == '__main__':
  init()
