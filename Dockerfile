FROM python:3.9.6-alpine3.14
LABEL author="Cauã Bernardino"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev python3-dev \
    musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
# Delete tmp
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D runner
RUN chown -R runner:runner /vol/
RUN chmod -R 755 /vol/web
USER runner