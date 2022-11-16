from django.db.models.signals import post_delete, post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver

from api import models


@receiver(post_save, sender = models.User)
def create_auth_token(sender, instance = None, created = False, **kwargs):
  # create an Auth token when new user (participant) joins
  if created:
    Token.objects.create(user = instance)
