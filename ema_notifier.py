# region imports
import os, django
import threading
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StressServer.settings")
django.setup()

from datetime import datetime
from datetime import timedelta
from random import randint
from api.models import Participant
from api.views import firebase_app
import firebase_admin
from firebase_admin import messaging


# endregion


def get_daily_notification_timings():
    notification_hour_range = (9, 23)
    delay_minutes_range = (30, 50)
    timing = datetime.now()
    timing = timing if timing.hour >= notification_hour_range[0] else timing.replace(hour=notification_hour_range[0], minute=0, second=0, microsecond=0)
    timings = []
    for i in range(20):
        if timing.hour > notification_hour_range[1]:
            break
        timing += timedelta(minutes=randint(delay_minutes_range[0], delay_minutes_range[1]))
        timings += [timing]
    return timings


def send_ema_notification(fcm_token):
    messaging.send(message=messaging.Message(
        notification=messaging.Notification(
            title="EMA time!",
            body=f'Please fill an EMA about your feelings and activity ☺'
        ),
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                title="EMA time!",
                body=f'Please fill an EMA about your feelings and activity ☺',
                channel_id='stressemaapp'
            )
        ),
        token=fcm_token
    ), app=firebase_app)


if __name__ == '__main__':
    if not firebase_app:
        firebase_app = firebase_admin.initialize_app(firebase_admin.credentials.Certificate('stressEmaApp.json'))

    now = datetime.now()
    then = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    threading.Timer((then - now).total_seconds(), send_ema_notification, args=(Participant.objects.get(id=10).fcm_token,)).start()

    day = datetime.now().day
    threads = set()
    while True:
        for participant in Participant.objects.all():
            if participant not in threads and participant.fcm_token:
                timings = get_daily_notification_timings()
                for dt in timings:
                    threading.Timer((dt - datetime.now()).total_seconds(), send_ema_notification, args=(participant.fcm_token,)).start()
                print(f'EMA for participant({participant.id}): {timings[0].strftime("%m/%d %H:%M")}, {", ".join([x.strftime("%H:%M") for x in timings[1:]])}')
                threads.add(participant)
        time.sleep(20 * 60)
        if day != datetime.now().day:
            day = datetime.now().day
            threads = {}
