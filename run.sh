export PYTHONUNBUFFERED=1
export PIPENV_VERBOSITY=-1
export DJANGO_SETTINGS_MODULE=dashboard.settings


echo 'Test goes first! running tests...'
if pipenv run python manage.py test; then
  echo 'Tests passed =)'
  echo 'Running the server...'
  
  # gunicorn version
  # exec pipenv run gunicorn dashboard.wsgi -c gunicorn.ini

  # docker version
  set -a
  source .env
  set +a
  exec sudo docker compose up -d --build
else
  echo 'Tests failed =('
fi