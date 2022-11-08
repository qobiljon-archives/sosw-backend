from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate
from django.urls import reverse as get_url

from api import models as mdl
from api import views as api
from api import serializers as srz

import json


class BaseTestCase(TestCase):

	def __init__(self, *args, **kwargs):
		super(BaseTestCase, self).__init__(*args, **kwargs)

		self.fac = APIRequestFactory()
		self.VALID_EMAIL = 'valid@email.com'
		self.VALID_PASSWORD = 'valid_password'

	def get_token(self):
		user_filter = mdl.User.objects.filter(username = self.VALID_EMAIL)
		if user_filter.exists(): user = user_filter[0]
		else: user = mdl.User.objects.create_user(
			username = self.VALID_EMAIL,
			email = self.VALID_EMAIL,
			password = self.VALID_PASSWORD,
		)
		return Token.objects.get(user = user)

	def auth(self, request):
		force_authenticate(request, user = self.get_token().user)
		return request
