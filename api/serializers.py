from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.utils.timezone import datetime as dt
from rest_framework.authtoken.models import Token

import time

from api import models as mdl
from api import services as svc


class UserSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(read_only = True)
  full_name = serializers.CharField(max_length = 64, required = True, allow_blank = False, allow_null = False)
  gender = serializers.CharField(max_length = 1, required = True, allow_blank = False, allow_null = False)
  date_of_birth = serializers.DateField(required = True, allow_null = False)
  fcm_token = serializers.CharField(max_length = 256, required = True, allow_blank = False, allow_null = False)

  class Meta:
    model = mdl.User
    fields = '__all__'


class ReadOnlyTokenSerializer(serializers.ModelSerializer):
  token = serializers.CharField(read_only = True, source = 'key')

  class Meta:
    model = Token
    fields = ['token']


class SelfReportSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(read_only = True)
  user = UserSerializer(read_only = True, allow_null = False)
  timestamp = serializers.IntegerField(allow_null = False, required = True)
  pss_control = serializers.IntegerField(allow_null = False, required = True)
  pss_confident = serializers.IntegerField(allow_null = False, required = True)
  pss_yourway = serializers.IntegerField(allow_null = False, required = True)
  pss_difficulties = serializers.IntegerField(allow_null = False, required = True)
  stresslvl = serializers.IntegerField(allow_null = False, required = True)
  social_settings = serializers.CharField(max_length = 16, allow_null = False, required = True)
  location = serializers.CharField(max_length = 16, allow_null = False, required = True)
  activity = serializers.CharField(max_length = 32, allow_null = False, required = True)

  def validate(self, attrs):
    before_start = dt(year = 2022, month = 11, day = 14)
    now = dt.now()
    ts = dt.fromtimestamp(attrs['timestamp']/1000)
    if ts < before_start or now < ts:
      raise ValidationError('Self-report timestamp cannot be before data collection start or in future!')

    acceptable_values = dict(
      pss_control = {0, 1, 2, 3, 4},   # 0-4 likert scale
      pss_confident = {0, 1, 2, 3, 4},
      pss_yourway = {0, 1, 2, 3, 4},
      pss_difficulties = {0, 1, 2, 3, 4},
      stresslvl = {0, 1, 2, 3, 4},
      social_settings = {'social', 'asocial'},
      location = {'home', 'work', 'restaurant', 'vehicle', 'other'},
      activity = {
        'studying_working', 'sleeping', 'relaxing', 'video_watching', 'class_meeting', 'eating_drinking', 'gaming',
        'conversing', 'goingtobed', 'calling_texting', 'justwokeup', 'riding_driving', 'other'
      },
    )

    for k, v in acceptable_values.items():
      if attrs[k] not in v:
        raise ValidationError(f'"{k}" can only be one of {v}')

    return attrs

  def create(self, validated_data):
    return svc.create_self_report_data(user = self.context['request'].user, **validated_data)

  class Meta:
    model = mdl.SelfReport
    fields = '__all__'


class ReadOnlySelfReportSerializer(serializers.ModelSerializer):
  timestamp = serializers.IntegerField(read_only = True)
  pss_control = serializers.IntegerField(read_only = True)
  pss_confident = serializers.IntegerField(read_only = True)
  pss_yourway = serializers.IntegerField(read_only = True)
  pss_difficulties = serializers.IntegerField(read_only = True)
  stresslvl = serializers.IntegerField(read_only = True)
  social_settings = serializers.CharField(read_only = True)
  location = serializers.CharField(read_only = True)
  activity = serializers.CharField(read_only = True)

  class Meta:
    model = mdl.SelfReport
    fields = [
      'timestamp', 'pss_control', 'pss_confident', 'pss_yourway', 'pss_difficulties', 'stresslvl', 'social_settings',
      'location', 'activity'
    ]


class OffBodySerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(read_only = True)
  user = UserSerializer(read_only = True, allow_null = False)
  timestamp = serializers.IntegerField(allow_null = False, required = True)
  is_off_body = serializers.BooleanField(allow_null = False)

  def validate(self, attrs):
    before_start = dt(year = 2022, month = 11, day = 14)
    now = dt.now()
    ts = dt.fromtimestamp(attrs['timestamp']/1000)
    if ts < before_start or now < ts:
      raise ValidationError('Self-report timestamp cannot be before data collection start or in future!')

    return attrs

  def create(self, validated_data):
    return svc.create_off_body_data(user = self.context['request'].user, **validated_data)

  class Meta:
    model = mdl.SelfReport
    fields = ['id', 'user', 'timestamp', 'is_off_body']


class LocationSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(read_only = True)
  user = UserSerializer(read_only = True, allow_null = False)
  timestamp = serializers.IntegerField(allow_null = False, required = True)
  latitude = serializers.FloatField(allow_null = False)
  longitude = serializers.FloatField(allow_null = False)
  accuracy = serializers.FloatField(allow_null = False)

  def create(self, validated_data):
    return svc.create_location_data(user = self.context['request'].user, **validated_data)

  class Meta:
    model = mdl.SelfReport
    fields = ['id', 'user', 'timestamp', 'latitude', 'longitude', 'accuracy']


class ScreenStateSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(read_only = True)
  user = UserSerializer(read_only = True, allow_null = False)
  timestamp = serializers.IntegerField(allow_null = False, required = True)
  screen_state = serializers.CharField(allow_null = False, max_length = 256)
  keyguard_restricted_input_mode = serializers.BooleanField(allow_null = False)

  def create(self, validated_data):
    return svc.create_screen_state_data(user = self.context['request'].user, **validated_data)

  class Meta:
    model = mdl.SelfReport
    fields = ['id', 'user', 'timestamp', 'screen_state', 'keyguard_restricted_input_mode']


class CalendarEventSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(read_only = True)
  user = UserSerializer(read_only = True, allow_null = False)
  event_id = serializers.CharField(allow_null = False, max_length = 256)
  title = serializers.CharField(allow_null = False, max_length = 256)
  start_ts = serializers.IntegerField(allow_null = False)
  end_ts = serializers.IntegerField(allow_null = False)
  event_location = serializers.CharField(allow_blank = True, allow_null = True, max_length = 256)

  def create(self, validated_data):
    return svc.create_calendar_event_data(user = self.context['request'].user, **validated_data)

  class Meta:
    model = mdl.SelfReport
    fields = ['id', 'user', 'event_id', 'title', 'start_ts', 'end_ts', 'event_location']


class CallLogSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(read_only = True)
  user = UserSerializer(read_only = True, allow_null = False)
  timestamp = serializers.IntegerField(allow_null = False, required = True)
  number = serializers.CharField(allow_null = False, max_length = 256)
  duration = serializers.CharField(allow_null = False, max_length = 256)
  call_type = serializers.CharField(allow_null = False, max_length = 256)

  def create(self, validated_data):
    return svc.create_call_log_data(user = self.context['request'].user, **validated_data)

  class Meta:
    model = mdl.SelfReport
    fields = ['id', 'user', 'timestamp', 'number', 'duration', 'call_type']


class ActivityTransitionSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(read_only = True)
  user = UserSerializer(read_only = True, allow_null = False)
  timestamp = serializers.IntegerField(allow_null = False, required = True)
  activity_type = serializers.CharField(allow_null = False, max_length = 256)
  transition_type = serializers.CharField(allow_null = False, max_length = 256)

  def create(self, validated_data):
    return svc.create_activity_transition_data(user = self.context['request'].user, **validated_data)

  class Meta:
    model = mdl.SelfReport
    fields = ['id', 'user', 'timestamp', 'activity_type', 'transition_type']
