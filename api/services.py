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


def create_location_data(
  user: mdl.User,
  timestamp: datetime,
  latitude: float,
  longitude: float,
  accuracy: float,
) -> mdl.OffBody:
  """ Creates a location data record / object """

  return mdl.Location.objects.create(
    user = user,
    timestamp = timestamp,
    latitude = latitude,
    longitude = longitude,
    accuracy = accuracy,
  )


def create_screen_state_data(
  user: mdl.User,
  timestamp: datetime,
  screen_state: str,
  keyguard_restricted_input_mode: bool,
) -> mdl.OffBody:
  """ Creates a screen state data record / object """

  return mdl.ScreenState.objects.create(
    user = user,
    timestamp = timestamp,
    screen_state = screen_state,
    keyguard_restricted_input_mode = keyguard_restricted_input_mode,
  )


def create_calendar_event_data(
  user: mdl.User,
  event_id: str,
  title: str,
  start_ts: int,
  end_ts: int,
  event_location: str,
) -> mdl.OffBody:
  """ Creates a calendar event data record / object """

  return mdl.CalendarEvent.objects.create(
    user = user,
    event_id = event_id,
    title = title,
    start_ts = start_ts,
    end_ts = end_ts,
    event_location = event_location,
  )


def create_call_log_data(
  user: mdl.User,
  timestamp: datetime,
  number: str,
  duration: str,
  call_type: str,
) -> mdl.OffBody:
  """ Creates a call log data record / object """

  return mdl.CallLog.objects.create(
    user = user,
    timestamp = timestamp,
    number = number,
    duration = duration,
    call_type = call_type,
  )


def create_activity_transition_data(
  user: mdl.User,
  timestamp: datetime,
  activity_type: str,
  transition_type: str,
) -> mdl.OffBody:
  """ Creates a activity transition data record / object """

  return mdl.ActivityTransition.objects.create(
    user = user,
    timestamp = timestamp,
    activity_type = activity_type,
    transition_type = transition_type,
  )
