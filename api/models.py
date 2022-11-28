from django.contrib.auth.models import AbstractUser

from django.db import models as mdl


class User(AbstractUser):
  full_name = mdl.CharField(max_length = 128)
  gender = mdl.CharField(max_length = 1)
  date_of_birth = mdl.DateField()
  fcm_token = mdl.CharField(max_length = 256, default = None, null = True)

  REQUIRED_FIELDS = ['full_name', 'gender', 'date_of_birth']


class SelfReport(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  timestamp = mdl.BigIntegerField(db_index = True)
  pss_control = mdl.IntegerField()
  pss_confident = mdl.IntegerField()
  pss_yourway = mdl.IntegerField()
  pss_difficulties = mdl.IntegerField()
  stresslvl = mdl.IntegerField()
  social_settings = mdl.CharField(max_length = 128)
  location = mdl.CharField(max_length = 128)
  activity = mdl.CharField(max_length = 128)


class OffBody(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  timestamp = mdl.BigIntegerField(db_index = True)
  is_off_body = mdl.BooleanField()


class Location(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  timestamp = mdl.BigIntegerField(db_index = True)
  latitude = mdl.FloatField()
  longitude = mdl.FloatField()
  accuracy = mdl.FloatField()


class ScreenState(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  timestamp = mdl.BigIntegerField(db_index = True)
  screen_state = mdl.CharField(max_length = 256)
  keyguard_restricted_input_mode = mdl.BooleanField()


class CallLog(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  timestamp = mdl.BigIntegerField(db_index = True)
  number = mdl.CharField(max_length = 256)
  duration = mdl.CharField(max_length = 256)
  call_type = mdl.CharField(max_length = 256)


class ActivityTransition(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  timestamp = mdl.BigIntegerField(db_index = True)
  activity_type = mdl.CharField(max_length = 256)
  transition_type = mdl.CharField(max_length = 256)


class CalendarEvent(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  event_id = mdl.CharField(db_index = True, max_length = 256)
  title = mdl.CharField(max_length = 256)
  start_ts = mdl.BigIntegerField()
  end_ts = mdl.BigIntegerField()
  event_location = mdl.CharField(max_length = 256)
