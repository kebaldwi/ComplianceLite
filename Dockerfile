FROM python:3.10

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip==20.2.3

RUN python3 --version && pip3 --version

WORKDIR /app
COPY ./app /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

RUN apt-get install openssl && apt install -y net-tools && apt-get install -y iputils-ping
RUN apt-get install -y cron

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app", "-w", "1", "--threads", "12"]
