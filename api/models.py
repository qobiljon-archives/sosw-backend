from django.contrib.auth.models import AbstractUser

from django.db import models as mdl


class User(AbstractUser):
	full_name = mdl.CharField(max_length = 128, required = True)
	date_of_birth = mdl.DateTimeField(required = True)
	fcm_token = mdl.CharField(max_length = 128, default = None)

	class Meta:
		unique_together = [
			'full_name',
			'date_of_birth',
		]


class PPG(mdl.Model):
	user = mdl.ForeignKey(to = 'User', null = True, on_delete = mdl.SET_NULL)
	timestamp = mdl.DateTimeField()
	light_intensity = mdl.FloatField()
	indexes = [mdl.Index(fields = [
		'user',
		'timestamp',
	])]


class Accelerometer(mdl.Model):
	user = mdl.ForeignKey(to = 'User', null = True, on_delete = mdl.SET_NULL)
	timestamp = mdl.DateTimeField()
	x = mdl.FloatField()
	y = mdl.FloatField()
	z = mdl.FloatField()
	indexes = [mdl.Index(fields = [
		'user',
		'timestamp',
	])]


class OffBody(mdl.Model):
	user = mdl.ForeignKey(to = 'User', null = True, on_delete = mdl.SET_NULL)
	timestamp = mdl.DateTimeField()
	is_off_body = mdl.BooleanField()
	indexes = [mdl.Index(fields = [
		'user',
		'timestamp',
	])]


class SelfReport(mdl.Model):
	user = mdl.ForeignKey(to = 'User', null = True, on_delete = mdl.SET_NULL)
	timestamp = mdl.DateTimeField()
	pss_control = mdl.IntegerField()
	pss_confident = mdl.IntegerField()
	pss_yourway = mdl.IntegerField()
	pss_difficulties = mdl.IntegerField()
	stresslvl = mdl.IntegerField()
	social_settings = mdl.CharField(max_length = 128)
	location = mdl.CharField(max_length = 128)
	activity = mdl.CharField(max_length = 128)
	indexes = [mdl.Index(fields = [
		'user',
		'timestamp',
	])]
