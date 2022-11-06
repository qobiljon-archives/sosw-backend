from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from firebase_admin import messaging
import firebase_admin

import json
import re

from api.models import Accelerometer
from django.http import JsonResponse
from api.models import Participant
from api.models import BVP
from api.models import SelfReport

firebase_app = None


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_register_api(request):
    new_participant = Participant.objects.create()
    return JsonResponse(data={'userId': new_participant.id})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_login_api(request):
    params = request.POST if 'userId' in request.POST else json.loads(request.body.decode())
    user_id = int(params['userId'])
    if Participant.objects.filter(id=user_id).exists():
        return JsonResponse(data={'success': True, 'userId': user_id})
    else:
        return JsonResponse(data={'success': False})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_set_fcm_token_api(request):
    params = request.POST if 'userId' in request.POST else json.loads(request.body.decode())
    user_id = int(params['userId'])
    if Participant.objects.filter(id=user_id).exists():
        p = Participant.objects.get(id=user_id)
        p.fcm_token = params['fcmToken']
        p.save()
        return JsonResponse(data={'success': True, 'fcmToken': p.fcm_token})
    else:
        return JsonResponse(data={'success': False})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_send_ema_notification_api(request):
    params = request.POST if 'userId' in request.POST else json.loads(request.body.decode())
    user_id = int(params['userId'])
    if Participant.objects.filter(id=user_id).exists():
        p = Participant.objects.get(id=user_id)
        if p.fcm_token:
            global firebase_app
            if not firebase_app:
                firebase_app = firebase_admin.initialize_app(firebase_admin.credentials.Certificate('fcm_secret.json'))
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
                token=p.fcm_token
            ), app=firebase_app)
            return JsonResponse(data={'success': True, 'fcm_token': p.fcm_token})
        else:
            return JsonResponse(data={'success': False})
    else:
        return JsonResponse(data={'success': False})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_submit_bvp_data_api(request):
    files = [x for x in request.POST if re.match(r'\d+[a-zA-Z]+\.csv', x)]
    user_id = int(request.POST['userId'])
    if Participant.objects.filter(id=user_id).exists():
        participant = Participant.objects.get(id=user_id)
        for file in files:
            for line in request.POST[file].split('\n'):
                cells = line[:-1].split(',')
                try:
                    timestamp = timezone.datetime.fromtimestamp(int(cells[0]) / 1000)
                    light_intensity = float(cells[1])
                    BVP.objects.create(
                        participant=participant,
                        timestamp=timestamp,
                        light_intensity=light_intensity
                    )
                except ValueError:
                    pass
        return JsonResponse(data={'success': True, 'fileNames': files})
    else:
        return JsonResponse(data={'success': False})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_submit_accelerometer_data_api(request):
    files = [x for x in request.POST if re.match(r'\d+[a-zA-Z]+\.csv', x)]
    user_id = int(request.POST['userId'])
    if Participant.objects.filter(id=user_id).exists():
        participant = Participant.objects.get(id=user_id)
        for file in files:
            for line in request.POST[file].split('\n'):
                cells = line[:-1].split(',')
                try:
                    timestamp = timezone.datetime.fromtimestamp(int(cells[0]) / 1000)
                    x, y, z = [float(x) for x in cells[1:]]
                    Accelerometer.objects.create(
                        participant=participant,
                        timestamp=timestamp,
                        x=x,
                        y=y,
                        z=z
                    )
                except ValueError:
                    pass
        return JsonResponse(data={'success': True, 'fileNames': files})
    else:
        return JsonResponse(data={'success': False})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_submit_ema_api(request):
    params = request.POST if 'pid' in request.POST else json.loads(request.body.decode())
    pid = int(params['pid'])
    self_report = params['self_report']

    if Participant.objects.filter(id=pid).exists():
        participant = Participant.objects.get(id=pid)
        SelfReport.objects.create(
            participant=participant,
            timestamp=self_report['timestamp'],
            pss_control=self_report['pss_control'],
            pss_confident=self_report['pss_confident'],
            pss_yourway=self_report['pss_yourway'],
            pss_difficulties=self_report['pss_difficulties'],
            stresslvl=self_report['stresslvl'],
            social_settings=self_report['social_settings'],
            location=self_report['location'],
            activity=self_report['activity'],
        )
        return JsonResponse(data={'success': True})
    else:
        return JsonResponse(data={'success': False})
