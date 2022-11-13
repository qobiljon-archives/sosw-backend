from typing import Iterable, List

from django.utils.timezone import datetime

from api import models as mdl


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
