from api.models import AccelerometerData
from api.models import SensingDataCount
from api.models import Participant
from api.models import BVPData
from api.models import EMAData

from django.contrib import admin


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'fcm_token', 'smartwatch_serial_number']


@admin.register(BVPData)
class BVPDataAdmin(admin.ModelAdmin):
	list_display = ['participant', 'timestamp', 'value']


@admin.register(AccelerometerData)
class AccelerometerDataAdmin(admin.ModelAdmin):
	list_display = ['participant', 'timestamp', 'x', 'y', 'z']


@admin.register(EMAData)
class EMADataAdmin(admin.ModelAdmin):
	list_display = ['participant', 'timestamp', 'response']


@admin.register(SensingDataCount)
class SensingDataCountAdmin(admin.ModelAdmin):
	list_display = ['participant', 'count']
