#!/usr/bin/env bash
set -o errexit

pip install -r eventify_backend/requirements.txt
cd eventify_backend

python manage.py collectstatic --no-input
python manage.py migrate