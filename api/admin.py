from api import models as mdl

from django.contrib import admin


@admin.register(mdl.User)
class UserAdmin(admin.ModelAdmin):
	list_display = [
		'full_name',
		'date_of_birth',
		'gender',
		'fcm_token',
	]


@admin.register(mdl.SelfReport)
class SelfReportAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'timestamp',
		'pss_control',
		'pss_confident',
		'pss_yourway',
		'pss_difficulties',
		'stresslvl',
		'social_settings',
		'location',
		'activity',
	]


@admin.register(mdl.OffBody)
class OffBodyAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'timestamp',
		'is_off_body',
	]