from typing import Optional, List
from api import models as mdl
from datetime import datetime as dt
from dateutil import tz


def user_exists(id: int = None, email: str = None) -> bool:
  if id:
    if not str(id).isdigit(): return False
    return mdl.User.objects.filter(id = int(id)).exists()
  if email:
    return mdl.User.objects.filter(email = str(email)).exists()
  return False


def get_user(id: int = None, email: str = None) -> Optional[mdl.User]:
  if id and str(id).isdigit() and mdl.User.objects.filter(id = int(id)).exists():
    return mdl.User.objects.get(id = int(id))
  if email and mdl.User.objects.filter(email = str(email)).exists():
    return mdl.User.objects.get(email = str(email))


def get_users(exclude_superusers = True) -> List[mdl.User]:
  if exclude_superusers:
    return mdl.User.objects.filter(is_superuser = False)
  return mdl.User.objects.all()


def get_fcm_token(id: int = None, email: str = None) -> mdl.User:
  if id: return mdl.User.objects.get(id = id).fcm_token
  if email: return mdl.User.objects.get(email = email).fcm_token
  return None


def get_self_reports(
  user: mdl.User,
  from_ts: Optional[int] = None,
  till_ts: Optional[int] = None,
) -> List[mdl.SelfReport]:
  """ Returns list of user's self-reports """

  if from_ts is None or till_ts is None:
    return mdl.SelfReport.objects.filter(user = user)
  return mdl.SelfReport.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).order_by('timestamp')


def get_first_timestamp(user: mdl.User) -> int:
  ans = float('inf')

  if mdl.SelfReport.objects.exists():
    ans = min(ans, mdl.SelfReport.objects.first().timestamp)
  if mdl.Location.objects.exists():
    ans = min(ans, mdl.Location.objects.first().timestamp)
  if mdl.ScreenState.objects.exists():
    ans = min(ans, mdl.ScreenState.objects.first().timestamp)
  if mdl.ActivityTransition.objects.exists():
    ans = min(ans, mdl.ActivityTransition.objects.first().timestamp)
  if mdl.ActivityRecognition.objects.exists():
    ans = min(ans, mdl.ActivityRecognition.objects.first().timestamp)

  return ans if ans != float('inf') else dt.now(tz = tz.gettz('Asia/Seoul'))


def get_ema_count(
  user: mdl.User,
  from_ts: Optional[int] = None,
  till_ts: Optional[int] = None,
) -> List[mdl.SelfReport]:
  """ Returns list of user's self-reports """

  if from_ts is None or till_ts is None:
    return mdl.SelfReport.objects.filter(user = user)
  return mdl.SelfReport.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).count()


def get_offbody_count(user: mdl.User, from_ts: int, till_ts: int) -> List[mdl.OffBody]:
  """ Returns list of off-body data """

  return mdl.OffBody.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).count()


def get_location_count(user: mdl.User, from_ts: int, till_ts: int) -> List[mdl.Location]:
  """ Returns list of locations data """

  return mdl.Location.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).count()


def get_screenstate_count(user: mdl.User, from_ts: int, till_ts: int) -> List[mdl.ScreenState]:
  """ Returns list of screen states data """

  return mdl.ScreenState.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).count()


def get_calllog_count(user: mdl.User, from_ts: int, till_ts: int) -> List[mdl.CallLog]:
  """ Returns list of call logs data """

  return mdl.CallLog.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).count()


def get_activitytransition_count(user: mdl.User, from_ts: int, till_ts: int) -> List[mdl.ActivityTransition]:
  """ Returns list of activity transitions data """

  return mdl.ActivityTransition.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).count()


def get_activityrecognitions_count(user: mdl.User, from_ts: int, till_ts: int) -> List[mdl.ActivityRecognition]:
  """ Returns list of activity transitions data """

  return mdl.ActivityRecognition.objects.filter(
    user = user,
    timestamp__gte = from_ts,
    timestamp__lte = till_ts,
  ).count()


def get_calendarevent_count(user: mdl.User, from_ts: int, till_ts: int) -> List[mdl.CalendarEvent]:
  """ Returns list of activity transitions data """

  return mdl.CalendarEvent.objects.filter(
    user = user,
    start_ts__gte = from_ts,
    end_ts__lte = till_ts,
  ).count()
