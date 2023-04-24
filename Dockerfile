FROM python:3.12.0a7-alpine3.17

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN apk add git #For development

RUN pip install -r requirements.txt
