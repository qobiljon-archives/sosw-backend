from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.models import InterbeatIntervalData
from api.models import LightIntensityData
from api.models import AccelerometerData
from api.models import EMAData
from django.http import JsonResponse
from api.models import Participant
from api import models
import firebase_admin
from firebase_admin import messaging
import json
import re

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
                firebase_app = firebase_admin.initialize_app(firebase_admin.credentials.Certificate('stressEmaApp.json'))
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
def handle_submit_data_api(request):
    files = [x for x in request.POST if re.match(r'\d+[a-zA-Z]+\.csv', x)]
    user_id = int(request.POST['userId'])
    if Participant.objects.filter(id=user_id).exists():
        participant = Participant.objects.get(id=user_id)
        for file in files:
            for line in request.POST[file].split('\n'):
                cells = line[:-1].split(',')
                try:
                    data_source = int(cells[0])
                    timestamp = timezone.datetime.fromtimestamp(int(cells[1]) / 1000)
                    if data_source == models.RRI_ID:
                        interbeat_interval = int(cells[2])
                        InterbeatIntervalData.objects.create(
                            participant=participant,
                            timestamp=timestamp,
                            interbeat_interval=interbeat_interval
                        )
                    if data_source == models.PPG_ID:
                        light_intensity = float(cells[2])
                        LightIntensityData.objects.create(
                            participant=participant,
                            timestamp=timestamp,
                            light_intensity=light_intensity
                        )
                    if data_source == models.ACC_ID:
                        x, y, z = [float(x) for x in cells[2:]]
                        AccelerometerData.objects.create(
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
    params = request.POST if 'userId' in request.POST else json.loads(request.body.decode())
    user_id = int(params['userId'])
    if Participant.objects.filter(id=user_id).exists():
        participant = Participant.objects.get(id=user_id)
        EMAData.objects.create(
            participant=participant,
            timestamp=timezone.now(),
            response=params['response']
        )
        return JsonResponse(data={'success': True})
    else:
        return JsonResponse(data={'success': False})
