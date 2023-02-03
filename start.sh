#!/bin/bash

if [ -n "${DOCKER_COMPOSE}" ]; then
    echo 'Checking for DB…'
    while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
        echo 'Waiting for DB…'
        sleep 1 # 1 second
    done
    echo 'DB ready.'

    echo 'Creating migrations for model changes…'
    python manage.py makemigrations
fi

echo 'Running migrations…'
python manage.py migrate

#python manage.py loaddata "$FIXTURES_FILE"
#
#if [ "${TEST_MODE}" == "True" ]; then
#    echo "Running tests"
#    coverage run manage.py test -v 3
#    coverage report
#else
#    echo "Running main placement-exams process"
#    python manage.py run
#fi
echo 'Running main application…'
python manage.py run
