FROM python:3

ENV PYTHONBUNUFFERED=1

WORKDIR /home/app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
