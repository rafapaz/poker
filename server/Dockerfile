FROM python:3.7-stretch

# File Author / Maintainer
MAINTAINER Rafael Paz Silva

RUN mkdir /app
RUN mkdir /var/log/app-logs
COPY . /app

RUN apt-get update && apt-get upgrade -y 
RUN pip install -r /app/requirements.txt

EXPOSE 6789

WORKDIR /app
ENTRYPOINT ["python", "server.py"]