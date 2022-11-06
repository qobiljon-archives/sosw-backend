from django.db import models


class Participant(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256, null=True, default=None)
    fcm_token = models.CharField(max_length=512, null=True, default=None)


class BVP(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    value = models.FloatField()
    indexes = [models.Index(fields=['user', 'timestamp'])]


class Accelerometer(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    indexes = [models.Index(fields=['user', 'timestamp'])]


class SelfReport(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    pss_control = models.IntegerField()
    pss_confident = models.IntegerField()
    pss_yourway = models.IntegerField()
    pss_difficulties = models.IntegerField()
    stresslvl = models.IntegerField()
    social_settings = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    activity = models.CharField(max_length=128)
    indexes = [models.Index(fields=['participant', 'timestamp'])]
