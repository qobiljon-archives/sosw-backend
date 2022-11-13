from os import environ
from os.path import join
from django import setup
import dotenv

environ['DJANGO_SETTINGS_MODULE'] = 'dashboard.settings'
dotenv.load_dotenv()
setup()

from django.test import TestCase
from django.utils.timezone import datetime as dt
from django.urls import reverse as get_url
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate

from api import models as mdl
from api import views as api

from os import listdir, remove
from os.path import exists


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

  def test_sign_up_api(self):
    url = get_url('signUpApi')
    view = api.SignUp.as_view()

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

  def test_api_with_token(self):
    self.get_token()
    res = api.SignIn.as_view()(self.fac.post(
      path = get_url('signInApi'),
      data = dict(
        email = self.username,
        password = self.password,
      ),
    ))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    token = res.data['token']

    url = get_url('submitSelfReportApi')
    view = api.InsertSelfReport.as_view()

    dummy_data = dict(
      timestamp = dt.now(),
      pss_control = 2,
      pss_confident = 2,
      pss_yourway = 2,
      pss_difficulties = 2,
      stresslvl = 2,
      social_settings = 'social',
      location = 'home',
      activity = 'other',
    )

    # invalid token
    res = view(self.fac.post(
      path = url,
      data = dummy_data,
      HTTP_AUTHORIZATION = f'Token {token}_invalid',
    ))
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # valid token
    res = view(self.fac.post(
      path = url,
      data = dummy_data,
      HTTP_AUTHORIZATION = f'Token {token}',
    ))
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class SelfReportTest(BaseTestCase):

  def test_insert(self):
    url = get_url('submitSelfReportApi')
    view = api.InsertSelfReport.as_view()
    _, token = self.get_token()

    # check tokens
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


class BVPTest(BaseTestCase):

  def __validate_files(self, test_files):
    files = set(listdir(path = environ['DATA_DUMP_DIR']))
    confirmations = list()
    for testName, testContent in test_files.items():
      self.assertIn(testName, files)
      filepath = join(environ['DATA_DUMP_DIR'], testName)
      if exists(filepath):
        with open(filepath, 'rb') as rb:
          confirmations.append(rb.read() == testContent)
        remove(filepath)
      else:
        confirmations.append(False)
    self.assertTrue(all(confirmations))

  def test_insert_valid(self):
    url = get_url('submitBVPApi')
    view = api.InsertBVP.as_view()

    test_files = {
      'bvp1.csv': b'1,2,3,4,5,6',
      'bvp2.csv': b'7,8,9,10,11',
      'bvp3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.__validate_files(test_files = test_files)

  def test_insert_empty(self):
    url = get_url('submitBVPApi')
    view = api.InsertBVP.as_view()

    test_files = dict()
    req = self.fac.post(
      path = url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_too_big(self):
    url = get_url('submitBVPApi')
    view = api.InsertBVP.as_view()

    test_files = {f'{x}.csv': b'dummy_content' for x in range(11)}
    req = self.fac.post(
      path = url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
