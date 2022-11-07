from django.db import models


class Participant(models.Model):
    full_name = models.CharField(max_length=256)
    date_of_birth = models.DateTimeField()
    fcm_token = models.CharField(max_length=512, null=True, default=None)

    class Meta:
        unique_together = ('full_name', 'date_of_birth',)


class BVP(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    light_intensity = models.FloatField()
    indexes = [models.Index(fields=['participant', 'timestamp'])]


class Accelerometer(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    indexes = [models.Index(fields=['participant', 'timestamp'])]


class OffBody(models.Model):
    participant = models.ForeignKey(to='Participant', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField()
    is_off_body = models.BooleanField()
    indexes = [models.Index(fields=['participant', 'timestamp'])]


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
