from api.models import Participant
from api.models import AccelerometerData
from api.models import InterbeatIntervalData
from api.models import LightIntensityData
from api.models import EMAData
from django.contrib import admin


@admin.register(Participant)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'smartwatch_serial_number']


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
