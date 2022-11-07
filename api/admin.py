from api.models import Accelerometer, OffBody
from api.models import Participant
from api.models import BVP
from api.models import SelfReport

from django.contrib import admin


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'date_of_birth', 'fcm_token']


@admin.register(BVP)
class BVPAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'light_intensity']


@admin.register(Accelerometer)
class AccelerometerAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'x', 'y', 'z']


@admin.register(OffBody)
class OffBodyAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'is_off_body']


@admin.register(SelfReport)
class SelfReportAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timestamp', 'pss_control', 'pss_confident', 'pss_yourway', 'pss_difficulties', 'stresslvl', 'social_settings', 'location', 'activity']
