from typing import Optional, List
from api import models as mdl


def user_exists(id: int = None, email: str = None) -> bool:
  if id: return mdl.User.objects.filter(id = id).exists()
  if email: return mdl.User.objects.filter(email = email).exists()
  return False


def get_fcm_token(id: int = None, email: str = None) -> mdl.User:
  if id: return mdl.User.objects.get(id = id).fcm_token
  if email: return mdl.User.objects.get(email = email).fcm_token
  return None


def get_self_reports(user: mdl.User) -> List[mdl.SelfReport]:
  """ Returns list of user's self-reports """

  return mdl.SelfReport.objects.filter(user = user)
