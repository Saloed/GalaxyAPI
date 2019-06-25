FROM python:3.7

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apt-transport-https && \
    apt-get install -y \
        git \
        nginx \
    	supervisor \
	    sqlite3

RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17 && \
    apt-get install -y --allow-unauthenticated unixodbc-dev


WORKDIR /usr/src/app

RUN pip3 install uwsgi

COPY requirements.txt ./

RUN pip3 install -r requirements.txt


RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx-app.conf /etc/nginx/sites-available/default
COPY supervisor-app.conf /etc/supervisor/conf.d/

COPY . .

ENV CONFIG="/etc/galaxy/config"

EXPOSE 80

CMD ["/bin/sh", "./run_server.sh"]
