FROM docker.io/library/python:3.8.6-alpine3.12

LABEL author="David Laganiere <my@email.org>"

# Create app directory
RUN mkdir -p /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY Pipfile Pipfile.lock manage.py webauth/ webtools/ /app/

RUN apk update && apk upgrade \
    && pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install --system --deploy --ignore-pipfile

# Expose port
EXPOSE 6000
