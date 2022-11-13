from django.test import TestCase
from django.utils.timezone import datetime as dt

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate
from django.urls import reverse as get_url

from api import models as mdl
from api import views as api


class BaseTestCase(TestCase):

  def __init__(self, *args, **kwargs):
    super(BaseTestCase, self).__init__(*args, **kwargs)
    self.fac = APIRequestFactory()

    self.username = 'example@email.com'
    self.password = 'example_password'

  def get_token(self) -> tuple[mdl.User, Token]:
    query_set = mdl.User.objects.filter(username = self.username)
    user = query_set[0] if query_set.exists() else mdl.User.objects.create_user(
      username = self.username,
      email = self.username,
      full_name = '홍길동',
      gender = 'M',
      date_of_birth = '1996-05-27',
      fcm_token = 'dummy',
      password = self.password,
    )
    return user, Token.objects.get(user = user)

  def force_auth(self, request):
    force_authenticate(request, user = self.get_token()[1].user)
    return request


class AuthTest(BaseTestCase):

  def test_register_api(self):
    url = get_url('registerApi')
    view = api.Register.as_view()

    # valid credentials
    mdl.User.objects.all().delete()
    res = view(
      self.fac.post(
        path = url,
        data = dict(
          email = 'example@gmail.com',
          full_name = '홍길동',
          gender = 'M',
          date_of_birth = '19960527',
          fcm_token = 'dummy',
          password = 'example_password',
        ),
      ))
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # invalid: already registered
    res = view(self.fac.post(url, dict(email = self.username, password = self.password)))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_sign_in_api(self):
    url = get_url('signInApi')
    view = api.SignIn.as_view()

    user, token = self.get_token()

    # empty req
    res = view(self.fac.post(url))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # missing email
    res = view(self.fac.post(url, dict(password = user.password)))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # missing password
    res = view(self.fac.post(url, dict(email = user.email)))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # invalid email
    res = view(self.fac.post(url, dict(email = f'a{user.email}', password = user.password)))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # invalid password
    res = view(self.fac.post(url, dict(email = user.email, password = f'p{user.password}')))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # valid credentials
    res = view(self.fac.post(url, dict(email = self.username, password = self.password)))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertIn('token', res.data)
    self.assertEqual(res.data['token'], token.key)


class SelfReportTest(BaseTestCase):

  def test_insert(self):
    url = get_url('submitSelfReportApi')
    view = api.InsertSelfReport.as_view()
    user, token = self.get_token()

    # check tokenss
    req = self.fac.post(
      path = url,
      data = dict(
        timestamp = dt.now(),
        pss_control = 2,
        pss_confident = 2,
        pss_yourway = 2,
        pss_difficulties = 2,
        stresslvl = 2,
        social_settings = 'social',
        location = 'home',
        activity = 'other',
      ),
      HTTP_AUTHORIZATION = f'Token {token.key}',
    )
    res = view(req)
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
