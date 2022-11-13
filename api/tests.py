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

    self.email = 'example@email.com'
    self.password = 'example_password'

  def get_token(self) -> tuple[mdl.User, Token]:
    query_set = mdl.User.objects.filter(username = self.email)
    user = query_set[0] if query_set.exists() else mdl.User.objects.create_user(
      username = self.email,
      email = self.email,
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


class SignUpTest(BaseTestCase):

  def __init__(self, *args, **kwargs):
    self.__url = get_url('signUpApi')
    self.__view = api.SignUp.as_view()
    super().__init__(*args, **kwargs)

  def test_valid(self):
    mdl.User.objects.all().delete()
    res = self.__view(
      self.fac.post(
        path = self.__url,
        data = dict(
          email = 'example@gmail.com',
          full_name = '홍길동',
          gender = 'M',
          date_of_birth = '19960527',
          password = 'example_password',
        ),
      ))
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_already_registered(self):
    mdl.User.objects.all().delete()
    mdl.User.objects.create_user(
      username = self.email,
      email = self.email,
      password = self.password,
      full_name = 'Dummy',
      gender = 'M',
      date_of_birth = '1996-05-27',
      fcm_token = 'dummy',
    )
    res = self.__view(self.fac.post(self.__url, dict(
      email = self.email,
      password = self.password,
    )))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class FcmTokenTest(BaseTestCase):

  def __init__(self, *args, **kwargs):
    self.__url = get_url('setFcmTokenApi')
    self.__view = api.SetFcmToken.as_view()
    super().__init__(*args, **kwargs)

  def test_update_fcm(self):
    user, _ = self.get_token()
    user.fcm_token = None
    user.save()

    new_token_value = 'new_dummy_fcm_token'
    req = self.fac.put(path = self.__url, data = dict(fcm_token = new_token_value))
    res = self.__view(self.force_auth(req))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(mdl.User.objects.get(email = self.email).fcm_token, new_token_value)


class SignInTest(BaseTestCase):

  def __init__(self, *args, **kwargs):
    self.__url = get_url('signInApi')
    self.__view = api.SignIn.as_view()
    super().__init__(*args, **kwargs)

  def test_valid(self):
    mdl.User.objects.all().delete()
    _, token = self.get_token()

    req = self.fac.post(
      path = self.__url,
      data = dict(email = self.email, password = self.password),
    )
    res = self.__view(request = req)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertIn('token', res.data)
    self.assertEqual(res.data['token'], token.key)

  def test_empty(self):
    mdl.User.objects.all().delete()
    self.get_token()
    res = self.__view(self.fac.post(self.__url))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_missing_email(self):
    mdl.User.objects.all().delete()
    self.get_token()
    res = self.__view(self.fac.post(self.__url, dict(password = self.password)))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_missing_password(self):
    mdl.User.objects.all().delete()
    self.get_token()
    res = self.__view(self.fac.post(self.__url, dict(email = self.email)))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_invalid_email(self):
    mdl.User.objects.all().delete()
    self.get_token()
    res = self.__view(self.fac.post(self.__url, dict(email = f'a{self.email}', password = self.password)))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_invalid_password(self):
    mdl.User.objects.all().delete()
    self.get_token()
    res = self.__view(self.fac.post(self.__url, dict(email = self.email, password = f'p{self.password}')))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TokenTest(BaseTestCase):

  def test_token_creation(self):
    mdl.User.objects.all().delete()
    Token.objects.all().delete()
    user = mdl.User.objects.create_user(
      username = self.email,
      email = self.email,
      password = self.password,
      full_name = 'Dummy',
      gender = 'M',
      date_of_birth = '1996-05-27',
      fcm_token = 'dummy',
    )
    self.assertTrue(Token.objects.filter(user = user).exists())

  def test_token_validity(self):
    mdl.User.objects.all().delete()
    Token.objects.all().delete()
    user = mdl.User.objects.create_user(
      username = self.email,
      email = self.email,
      password = self.password,
      full_name = 'Dummy',
      gender = 'M',
      date_of_birth = '1996-05-27',
      fcm_token = 'dummy',
    )
    self.assertTrue(Token.objects.filter(user = user).exists())
    token1 = Token.objects.get(user = user)

    res = api.SignIn.as_view()(self.fac.post(
      path = get_url('signInApi'),
      data = dict(
        email = self.email,
        password = self.password,
      ),
    ))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertIn('token', res.data)
    token2 = res.data['token']

    self.assertEqual(token1.key, token2)

  def test_valid_token(self):
    url = get_url('submitSelfReportApi')
    view = api.InsertSelfReport.as_view()
    _, token = self.get_token()

    res = view(
      self.fac.post(
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
      ))
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_invalid_token(self):
    url = get_url('submitSelfReportApi')
    view = api.InsertSelfReport.as_view()
    _, token = self.get_token()

    res = view(
      self.fac.post(
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
        HTTP_AUTHORIZATION = f'Token {token.key}_invalid',
      ))
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class SelfReportTest(BaseTestCase):

  def __init__(self, *args, **kwargs):
    self.__url = get_url('submitSelfReportApi')
    self.__view = api.InsertSelfReport.as_view()
    super().__init__(*args, **kwargs)

  def test_insert_valid(self):
    url = get_url('submitSelfReportApi')
    view = api.InsertSelfReport.as_view()
    _, token = self.get_token()

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
    )
    res = view(self.force_auth(req))
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_insert_invalid_likert_range(self):
    for likertCol in ['pss_control', 'pss_confident', 'pss_yourway', 'pss_difficulties', 'stresslvl']:
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

      dummy_data[likertCol] = -1   # must be one of : [0,1,2,3,4]
      req = self.fac.post(path = self.__url, data = dummy_data)
      res = self.__view(self.force_auth(req))
      self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

      dummy_data[likertCol] = 5   # must be one of : [0,1,2,3,4]
      req = self.fac.post(path = self.__url, data = dummy_data)
      res = self.__view(self.force_auth(req))
      self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_invalid_social_settings(self):
    req = self.fac.post(
      path = self.__url,
      data = dict(
        timestamp = dt.now(),
        pss_control = 2,
        pss_confident = 2,
        pss_yourway = 2,
        pss_difficulties = 2,
        stresslvl = 2,
        social_settings = 'notsocial',   # must be one of : ['social', 'asocial']
        location = 'home',
        activity = 'other',
      ),
    )
    res = self.__view(self.force_auth(req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_invalid_location(self):
    req = self.fac.post(
      path = self.__url,
      data = dict(
        timestamp = dt.now(),
        pss_control = 2,
        pss_confident = 2,
        pss_yourway = 2,
        pss_difficulties = 2,
        stresslvl = 2,
        social_settings = 'social',
        location = 'apartment',   # must be one of : ['home', 'work', 'restaurant', 'vehicle', 'other']
        activity = 'other',
      ),
    )
    res = self.__view(self.force_auth(req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_invalid_activity(self):
    req = self.fac.post(
      path = self.__url,
      data = dict(
        timestamp = dt.now(),
        pss_control = 2,
        pss_confident = 2,
        pss_yourway = 2,
        pss_difficulties = 2,
        stresslvl = 2,
        social_settings = 'social',
        location = 'home',
        activity =
        'bowling',   # must be one of : ['studying_working', 'sleeping', 'relaxing', 'video_watching', 'class_meeting', 'eating_drinking', 'gaming', 'conversing', 'goingtobed', 'calling_texting', 'justwokeup', 'riding_driving', 'other']
      ),
    )
    res = self.__view(self.force_auth(req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PPGTest(BaseTestCase):
  from api.views import DATA_DUMP_DIR

  def __init__(self, *args, **kwargs):
    self.__url = get_url('submitPPGApi')
    self.__view = api.InsertPPG.as_view()
    super().__init__(*args, **kwargs)

  def __validate_files(self, test_files):
    dirpath = join(self.DATA_DUMP_DIR, self.email)
    self.assertTrue(exists(dirpath))

    files = set(listdir(path = dirpath))
    confirmations = list()
    for testName, testContent in test_files.items():
      self.assertIn(testName, files)
      filepath = join(dirpath, testName)
      if exists(filepath):
        with open(filepath, 'rb') as rb:
          confirmations.append(rb.read() == testContent)
        remove(filepath)
      else:
        confirmations.append(False)
    self.assertTrue(all(confirmations))

  def test_insert_valid(self):
    test_files = {
      'ppg1.csv': b'1,2,3,4,5,6',
      'ppg2.csv': b'7,8,9,10,11',
      'ppg3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.__validate_files(test_files = test_files)

  def test_insert_bad_name(self):
    test_files = {
      'ppg1.csv': b'1,2,3,4,5,6',
      'ppg2.csv': b'7,8,9,10,11',
      'acc3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    test_files = {
      'ppg1.csv': b'1,2,3,4,5,6',
      'ppg2.csv': b'7,8,9,10,11',
      'offbody3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_empty(self):
    test_files = dict()
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_too_big(self):
    test_files = {f'ppg{x}.csv': b'dummy_content' for x in range(11)}
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AccTest(BaseTestCase):
  from api.views import DATA_DUMP_DIR

  def __init__(self, *args, **kwargs):
    self.__url = get_url('submitAccApi')
    self.__view = api.InsertAcc.as_view()
    super().__init__(*args, **kwargs)

  def __validate_files(self, test_files):
    dirpath = join(self.DATA_DUMP_DIR, self.email)
    self.assertTrue(exists(dirpath))

    files = set(listdir(path = dirpath))
    confirmations = list()
    for testName, testContent in test_files.items():
      self.assertIn(testName, files)
      filepath = join(dirpath, testName)
      if exists(filepath):
        with open(filepath, 'rb') as rb:
          confirmations.append(rb.read() == testContent)
        remove(filepath)
      else:
        confirmations.append(False)
    self.assertTrue(all(confirmations))

  def test_insert_valid(self):
    test_files = {
      'acc1.csv': b'1,2,3,4,5,6',
      'acc2.csv': b'7,8,9,10,11',
      'acc3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.__validate_files(test_files = test_files)

  def test_insert_bad_name(self):
    test_files = {
      'acc1.csv': b'1,2,3,4,5,6',
      'acc2.csv': b'7,8,9,10,11',
      'ppg3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    test_files = {
      'acc1.csv': b'1,2,3,4,5,6',
      'acc2.csv': b'7,8,9,10,11',
      'offbody3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_empty(self):
    test_files = dict()
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_too_big(self):
    test_files = {f'acc{x}.csv': b'dummy_content' for x in range(11)}
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class OffBodyTest(BaseTestCase):
  from api.views import DATA_DUMP_DIR

  def __init__(self, *args, **kwargs):
    self.__url = get_url('submitOffBodyApi')
    self.__view = api.InsertOffBody.as_view()
    super().__init__(*args, **kwargs)

  def __validate_files(self, test_files):
    dirpath = join(self.DATA_DUMP_DIR, self.email)
    self.assertTrue(exists(dirpath))

    files = set(listdir(path = dirpath))
    confirmations = list()
    for testName, testContent in test_files.items():
      self.assertIn(testName, files)
      filepath = join(dirpath, testName)
      if exists(filepath):
        with open(filepath, 'rb') as rb:
          confirmations.append(rb.read() == testContent)
        remove(filepath)
      else:
        confirmations.append(False)
    self.assertTrue(all(confirmations))

  def test_insert_valid(self):
    test_files = {
      'offbody1.csv': b'1,2,3,4,5,6',
      'offbody2.csv': b'7,8,9,10,11',
      'offbody3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.__validate_files(test_files = test_files)

  def test_insert_bad_name(self):
    test_files = {
      'offbody1.csv': b'1,2,3,4,5,6',
      'offbody2.csv': b'7,8,9,10,11',
      'ppg3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    test_files = {
      'offbody1.csv': b'1,2,3,4,5,6',
      'offbody2.csv': b'7,8,9,10,11',
      'acc3.csv': b'12,13,14,15',
    }
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_empty(self):
    test_files = dict()
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_insert_too_big(self):
    test_files = {f'offbody{x}.csv': b'dummy_content' for x in range(11)}
    req = self.fac.post(
      path = self.__url,
      data = dict(files = [SimpleUploadedFile(name = name, content = content) for name, content in test_files.items()]),
    )
    res = self.__view(self.force_auth(request = req))
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
