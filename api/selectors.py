from typing import Optional
from api import models as mdl


def user_exists(full_name: str, date_of_birth: str) -> bool:
	return mdl.Participant.objects.filter(full_name=full_name, date_of_birth=date_of_birth).exists()
