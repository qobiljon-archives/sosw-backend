from django.contrib.auth.models import AbstractUser

from django.db import models as mdl


class User(AbstractUser):
  full_name = mdl.CharField(max_length = 128)
  gender = mdl.CharField(max_length = 1)
  date_of_birth = mdl.DateField()
  fcm_token = mdl.CharField(max_length = 128, default = None, null = True)

  REQUIRED_FIELDS = ['full_name', 'gender', 'date_of_birth']


class SelfReport(mdl.Model):
  id = mdl.AutoField(primary_key = True)
  user = mdl.ForeignKey(to = 'User', on_delete = mdl.CASCADE, db_index = True)
  timestamp = mdl.DateTimeField(db_index = True)
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
  timestamp = mdl.DateTimeField(db_index = True)
  is_off_body = mdl.BooleanField()
