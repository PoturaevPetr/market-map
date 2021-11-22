FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /srv/www
COPY requirements.txt /srv/www/
RUN apt-get update && apt-get -y install libgeos-c1v5 protobuf-compiler && apt-get install nginx
RUN /etc/init.d/nginx start
RUN pip install -r requirements.txt
COPY . /srv/www/