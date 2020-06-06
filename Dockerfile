FROM docker.io/library/python:3.8.3-alpine3.11

MAINTAINER David Laganiere <my@email.org>

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "python", "./app.py" ]
