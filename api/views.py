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
	args = json.loads(request.body.decode())
	assert all(x in args for x in ['full_name', 'date_of_birth', 'fcm_token'])

	date_of_birth = dt.strptime(args['date_of_birth'], '%Y%m%d')
	if not Participant.objects.filter(full_name=args['full_name'], date_of_birth=date_of_birth).exists():
		Participant.objects.create(full_name=args['full_name'], date_of_birth=date_of_birth, fcm_token=args['fcm_token'])
	else:
		participant = Participant.objects.get(full_name=args['full_name'], date_of_birth=date_of_birth)
		participant.fcm_token = args['fcm_token']
		participant.save()


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_send_ema_push_api(request):
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
					title="Stress report time!",
					body="Please log your current situation and stress levels."
				),
				android=messaging.AndroidConfig(
					priority='high',
					notification=messaging.AndroidNotification(
						title="Stress report time!",
						body="Please log your current situation and stress levels.",
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
	args = json.loads(request.body.decode())
	if any(x not in args for x in ['full_name', 'date_of_birth', 'self_report']) or not is_valid_date(args['date_of_birth']):
		return JsonResponse(data={'success': False})

	date_of_birth = str2date(args['date_of_birth'])
	if Participant.objects.filter(full_name=args['full_name'], date_of_birth=date_of_birth).exists():
		participant = Participant.objects.get(full_name=args['full_name'], date_of_birth=date_of_birth)
		SelfReport.objects.create(
			participant=participant,
			timestamp=dt.fromtimestamp(int(args['self_report']['timestamp']) / 1000),
			pss_control=args['self_report']['pss_control'],
			pss_confident=args['self_report']['pss_confident'],
			pss_yourway=args['self_report']['pss_yourway'],
			pss_difficulties=args['self_report']['pss_difficulties'],
			stresslvl=args['self_report']['stresslvl'],
			social_settings=args['self_report']['social_settings'],
			location=args['self_report']['location'],
			activity=args['self_report']['activity'],
		)
		return JsonResponse(data={'success': True})
	else:
		return JsonResponse(data={'success': False})
