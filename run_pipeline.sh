#!/usr/bin/env sh


run_critical() {
	echo "+ $@"
	$@
	if [ $? -ne 0 ]; then
		echo [!] Checks failed!
		exit 1
	fi
}

run_critical flake8 --max-line-length=120 --exclude=.git,.venv,core/migrations,users/migrations ./
run_critical pylint --ignore-patterns=.git,.venv,core/migrations,users/migrations,manage ./*.py

set -x

bandit -r ./core ./gradify ./users
coverage run --omit="core/migrations/*","users/migrations/*","manage.py","core/tests/*" --source="."  manage.py test --settings gradify.settings.ci
coverage report
