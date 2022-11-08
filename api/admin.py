from api import models as mdl

from django.contrib import admin


@admin.register(mdl.User)
class UserAdmin(admin.ModelAdmin):
	list_display = ['full_name', 'date_of_birth', 'fcm_token']


@admin.register(mdl.PPG)
class BVPAdmin(admin.ModelAdmin):
	list_display = ['user', 'timestamp', 'light_intensity']


@admin.register(mdl.Accelerometer)
class AccelerometerAdmin(admin.ModelAdmin):
	list_display = ['user', 'timestamp', 'x', 'y', 'z']


@admin.register(mdl.OffBody)
class OffBodyAdmin(admin.ModelAdmin):
	list_display = ['user', 'timestamp', 'is_off_body']


@admin.register(mdl.SelfReport)
class SelfReportAdmin(admin.ModelAdmin):
	list_display = ['user', 'timestamp', 'pss_control', 'pss_confident', 'pss_yourway', 'pss_difficulties', 'stresslvl', 'social_settings', 'location', 'activity']
