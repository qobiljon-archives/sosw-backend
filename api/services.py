from typing import Iterable, List

from django.utils.timezone import datetime

from datetime import datetime

from api import models as mdl


def create_participant(
	full_name: str,
	date_of_birth: str,
) -> mdl.Participant:
	""" Creates a participant object """

	return mdl.Participant.objects.create(
		full_name = full_name,
		date_of_birth = date_of_birth,
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

	return mdl.SelfReport.objects.create({
		'a': 1,
		'b': 2,
	})


def bulk_create_self_reports(self_reports: Iterable[mdl.SelfReport]) -> List[mdl.BVP]:
	return mdl.SelfReport.objects.bulk_create(self_reports)


def create_bvp_data(**bvp_data) -> mdl.BVP:
	return mdl.BVP.objects.create(**bvp_data)


def bulk_create_bvp_data(bvp: Iterable[mdl.BVP]) -> List[mdl.BVP]:
	return mdl.BVP.objects.bulk_create(bvp)


def create_acc_data(**acc_data) -> mdl.Accelerometer:
	return mdl.Accelerometer.objects.create(**acc_data)
