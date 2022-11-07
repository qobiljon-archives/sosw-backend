from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from firebase_admin import messaging
import firebase_admin

from datetime import datetime as dt
import json
import re

from api.models import Accelerometer
from django.http import JsonResponse
from api.models import Participant
from api.models import BVP
from api.models import SelfReport
from api.utils import is_valid_date, str2date

firebase_app = None


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_auth_api(request):
    res = dict()

    args = json.loads(request.body.decode())
    assert all(x in args for x in ['full_name', 'date_of_birth', 'fcm_token'])

    date_of_birth = dt.strptime(args['date_of_birth'], '%Y%m%d')
    if not Participant.objects.filter(full_name=args['full_name'], date_of_birth=date_of_birth).exists():
        Participant.objects.create(full_name=args['full_name'], date_of_birth=date_of_birth, fcm_token=args['fcm_token'])
    else:
        participant = Participant.objects.get(full_name=args['full_name'], date_of_birth=date_of_birth)
        participant.fcm_token = args['fcm_token']
        participant.save()

    return JsonResponse(data=res)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_auth_watch_api(request):
    res = dict()

    args = json.loads(request.body.decode())
    assert all(x in args for x in ['full_name', 'date_of_birth'])

    date_of_birth = dt.strptime(args['date_of_birth'], '%Y%m%d')
    if Participant.objects.filter(full_name=args['full_name'], date_of_birth=date_of_birth).exists():
        res['success'] = True
    else:
        res['success'] = False

    return JsonResponse(data=res)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_send_ema_push_api(request):
    res = dict()

    args = request.POST if 'pid' in request.POST else json.loads(request.body.decode())
    pid = int(args['pid'])
    if Participant.objects.filter(id=pid).exists():
        participant = Participant.objects.get(id=pid)
        if participant.fcm_token:
            global firebase_app
            if not firebase_app:
                firebase_app = firebase_admin.initialize_app(firebase_admin.credentials.Certificate('fcm_secret.json'))
            messaging.send(message=messaging.Message(
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        title="Stress report time!",
                        body="Please log your current situation and stress levels.",
                        channel_id='sosw.app.push'
                    )
                ),
                token=participant.fcm_token
            ), app=firebase_app)
            res['success'] = True
            res['fcm_token'] = participant.fcm_token
        else:
            res['success'] = False
    else:
        res['success'] = False

    return JsonResponse(data=res)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_submit_bvp_data_api(request):
    res = dict()

    args = json.loads(request.body.decode())
    date_of_birth = dt.strptime(args['date_of_birth'], '%Y%m%d')
    if Participant.objects.filter(full_name=args['full_name'], date_of_birth=date_of_birth).exists():
        for bvp_data in args['acc_data']:
            try:
                BVP.objects.create(
                    timestamp=timezone.datetime.fromtimestamp(int(bvp_data['timestamp']) / 1000),
                    light_intensity=int(bvp_data['light_intensity'])
                )
            except ValueError:
                pass
        res['success'] = True
    else:
        res['success'] = False

    return JsonResponse(data=res)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_submit_accelerometer_data_api(request):
    res = dict()

    args = json.loads(request.body.decode())
    date_of_birth = dt.strptime(args['date_of_birth'], '%Y%m%d')
    if Participant.objects.filter(full_name=args['full_name'], date_of_birth=date_of_birth).exists():
        for acc_data in args['acc_data']:
            try:
                Accelerometer.objects.create(
                    timestamp=timezone.datetime.fromtimestamp(int(acc_data['timestamp']) / 1000),
                    x=float(acc_data['x']),
                    y=float(acc_data['y']),
                    z=float(acc_data['z'])
                )
            except ValueError:
                pass
        res['success'] = True
    else:
        res['success'] = False

    return JsonResponse(data=res)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_submit_self_report_api(request):
    res = dict()

    args = json.loads(request.body.decode())
    date_of_birth = str2date(args['date_of_birth'])

    if Participant.objects.filter(full_name=args['full_name'], date_of_birth=date_of_birth).exists():
        participant = Participant.objects.get(full_name=args['full_name'], date_of_birth=date_of_birth)
        for self_report in args['self_reports']:
            SelfReport.objects.create(
                participant=participant,
                timestamp=dt.fromtimestamp(int(self_report['timestamp']) / 1000),
                pss_control=self_report['pss_control'],
                pss_confident=self_report['pss_confident'],
                pss_yourway=self_report['pss_yourway'],
                pss_difficulties=self_report['pss_difficulties'],
                stresslvl=self_report['stresslvl'],
                social_settings=self_report['social_settings'],
                location=self_report['location'],
                activity=self_report['activity']
            )
        res['success'] = True
    else:
        res['success'] = False

    return JsonResponse(data=res)
