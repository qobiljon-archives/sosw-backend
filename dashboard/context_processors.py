from os import environ


def export_vars(_):
	return dict(
		STATIC_HOST=environ['STATIC_HOST'],
		STATIC_PORT=environ['STATIC_PORT'],
	)
