from api.models import Participant
from api.models import AccelerometerData
from api.models import InterbeatIntervalData
from api.models import LightIntensityData
from api.models import EMAData
from api.models import SensingDataCount
from django.contrib import admin


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'fcm_token', 'smartwatch_serial_number']


@admin.register(InterbeatIntervalData)
class InterbeatIntervalDataAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'interbeat_interval']


@admin.register(LightIntensityData)
class LightIntensityDataAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'light_intensity']


@admin.register(AccelerometerData)
class AccelerometerDataAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'x', 'y', 'z']


@admin.register(EMAData)
class EMADataAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'response']


@admin.register(SensingDataCount)
class SensingDataCountAdmin(admin.ModelAdmin):
    list_display = ['participant', 'count']
