#!/bin/sh
j2 /templates/nginx.conf.j2 >  /etc/nginx/sites-available/default
python manage.py migrate && python manage.py collectstatic
exec "$@"