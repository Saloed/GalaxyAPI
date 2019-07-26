FROM python:3.7

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apt-transport-https && \
    apt-get install -y \
        git \
        nginx \
    	supervisor \
	    sqlite3

RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg && \
    curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get --allow-unauthenticated update && \
    ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17 && \
    apt-get install -y --allow-unauthenticated unixodbc-dev


WORKDIR /usr/src/app

RUN pip3 install uwsgi j2cli

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY nginx.conf.j2 /templates/
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

COPY supervisor-app.conf /etc/supervisor/conf.d/

RUN apt-get install -y redis-server
COPY redis.conf /etc/redis/redis.conf

COPY configuration_entrypoint.sh /

COPY . .

ENV CONFIG="/etc/galaxy/config"

ENTRYPOINT ["/configuration_entrypoint.sh"]
CMD ["supervisord", "-n"]
