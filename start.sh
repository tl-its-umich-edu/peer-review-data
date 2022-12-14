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

echo 'Running main application…'
python manage.py run
