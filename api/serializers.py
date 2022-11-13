from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.utils.timezone import datetime as dt
from rest_framework.authtoken.models import Token

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
    fields = ['email', 'full_name', 'gender', 'date_of_birth', 'fcm_token']


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
    fields = [
      'id', 'user', 'timestamp', 'pss_control', 'pss_confident', 'pss_yourway', 'pss_difficulties', 'stresslvl',
      'social_settings', 'location', 'activity'
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
