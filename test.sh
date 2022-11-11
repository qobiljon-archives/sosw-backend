export PIPENV_VERBOSITY=-1
# exec pipenv run ./manage.py test
echo 'Running tests...'
if pipenv run coverage run --source='.' manage.py test api; then
  echo 'OK, reporting test coverage...'
  pipenv run coverage report
else
  echo 'Testing failed =('
fi
