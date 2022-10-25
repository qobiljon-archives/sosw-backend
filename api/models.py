from django.db import models


class Participant(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=256, null=True, default=None)
	fcm_token = models.CharField(max_length=512, null=True, default=None)
	smartwatch_serial_number = models.CharField(max_length=256, null=True, default=None)


class BVPData(models.Model):
	participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
	timestamp = models.DateTimeField()
	value = models.FloatField()
	indexes = [models.Index(fields=['user', 'timestamp'])]


class AccelerometerData(models.Model):
	participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
	timestamp = models.DateTimeField()
	x = models.FloatField()
	y = models.FloatField()
	z = models.FloatField()
	indexes = [models.Index(fields=['user', 'timestamp'])]


class EMAData(models.Model):
	participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
	timestamp = models.DateTimeField()
	response = models.CharField(max_length=2048)
	indexes = [models.Index(fields=['user', 'timestamp'])]


class SensingDataCount(models.Model):
	participant = models.OneToOneField(to='Participant', on_delete=models.CASCADE)
	count = models.IntegerField(default=0)
	last_timestamp = models.DateTimeField()
