from typing import Iterable, List

from django.utils.timezone import datetime

from api import models as mdl


def create_user(
  username: str,
  email: str,
  full_name: str,
  gender: str,
  date_of_birth: str,
  password: str,
) -> mdl.User:
  """ Creates a user object """

  return mdl.User.objects.create_user(
    username = username,
    email = email,
    full_name = full_name,
    gender = gender,
    date_of_birth = date_of_birth,
    password = password,
  )


def create_self_report_data(
  user: mdl.User,
  timestamp: datetime,
  pss_control: int,
  pss_confident: int,
  pss_yourway: int,
  pss_difficulties: int,
  stresslvl: int,
  social_settings: str,
  location: str,
  activity: str,
) -> mdl.SelfReport:
  """ Creates a self-report object """

  return mdl.SelfReport.objects.create(
    user = user,
    timestamp = timestamp,
    pss_control = pss_control,
    pss_confident = pss_confident,
    pss_yourway = pss_yourway,
    pss_difficulties = pss_difficulties,
    stresslvl = stresslvl,
    social_settings = social_settings,
    location = location,
    activity = activity,
  )


def create_off_body_data(
  user: mdl.User,
  timestamp: datetime,
  is_off_body: bool,
) -> mdl.OffBody:
  """ Creates an off-body data record / object """

  return mdl.OffBody.objects.create(
    user = user,
    timestamp = timestamp,
    is_off_body = is_off_body,
  )
