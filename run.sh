 docker run -p 8000:80 --name galaxy-api -v $PWD/galaxy_api.ini:/etc/galaxy/config galaxy-api