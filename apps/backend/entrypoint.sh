#!/bin/bash
# прерывание выполнения при любой ошибке
set -e

python manage.py collectstatic --noinput

# выполнить то, что было передано в CMD или в command (docker-compose)
exec "$@"