import datetime

import pytz
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.models import InterbeatIntervalData
from api.models import LightIntensityData
from api.models import AccelerometerData
from django.http import JsonResponse
from django.shortcuts import render
from api.models import Participant
from api import models
import re


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_register_api(request):
    new_participant = Participant.objects.create()
    return JsonResponse(data={'userId': new_participant.id})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_login_api(request):
    user_id = int(request.POST['userId'])
    if Participant.objects.filter(id=user_id).exists():
        return JsonResponse(data={'success': True, 'userId': user_id})
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
