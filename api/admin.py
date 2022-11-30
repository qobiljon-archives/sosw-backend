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


@admin.register(mdl.Location)
class LocationAdmin(admin.ModelAdmin):
  list_display = [
    'user',
    'timestamp',
    'latitude',
    'longitude',
    'accuracy',
  ]


@admin.register(mdl.ScreenState)
class ScreenStateAdmin(admin.ModelAdmin):
  list_display = [
    'user',
    'timestamp',
    'screen_state',
    'keyguard_restricted_input_mode',
  ]


@admin.register(mdl.CallLog)
class CallLogAdmin(admin.ModelAdmin):
  list_display = [
    'user',
    'timestamp',
    'number',
    'duration',
    'call_type',
  ]


@admin.register(mdl.ActivityTransition)
class ActivityTransitionAdmin(admin.ModelAdmin):
  list_display = [
    'user',
    'timestamp',
    'activity',
    'transition',
  ]


@admin.register(mdl.ActivityRecognition)
class ActivityRecognitionAdmin(admin.ModelAdmin):
  list_display = [
    'user',
    'timestamp',
    'activity',
    'confidence',
  ]


@admin.register(mdl.CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
  list_display = [
    'user',
    'event_id',
    'title',
    'start_ts',
    'end_ts',
    'event_location',
  ]
