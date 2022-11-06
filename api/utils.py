from datetime import datetime as dt
import re


def is_valid_date(date_str: str) -> bool:
	if not re.match(r'^\d{8}$', date_str): return False

	try:
		date = dt.strptime(date_str, '%Y%m%d')
		if date >= dt.now(): return False
	except ValueError:
		return False

	return True


def str2date(date_str: str) -> dt:
	return dt.strptime(date_str, '%Y%m%d')
