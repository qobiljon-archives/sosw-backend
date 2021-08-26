from django.db import models

RRI_ID = 1
PPG_ID = 2
ACC_ID = 3


# Create your models here.
class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, null=True, default=None)
    smartwatch_serial_number = models.CharField(max_length=256, null=True, default=None)


class InterbeatIntervalData(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    interbeat_interval = models.IntegerField()
    indexes = [models.Index(fields=['user', 'timestamp'])]


class LightIntensityData(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    light_intensity = models.FloatField()
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
