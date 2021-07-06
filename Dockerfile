FROM python:3.9.6-alpine3.14
LABEL author="Cauã Bernardino"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D runner
USER runner