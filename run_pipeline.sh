#!/usr/bin/env sh

set -x

flake8 --max-line-length=120 --exclude=.git,.venv,users/migrations,core/migrations ./
pylint --ignore-patterns=.git,.venv,core/migrations,users/migrations,manage ./*.py
bandit -r ./core ./users ./gradify
coverage run --omit="core/migrations/*","users/migrations/*","manage.py","core/tests/*" --source="."  manage.py test --settings gradify.settings.ci
coverage report

