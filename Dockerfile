FROM docker.io/library/python:3.8.3-alpine3.11

LABEL author="David Laganiere <my@email.org>"

ENV PYTHONUNBUFFERED 1

# To be able to run flask simply with 'flask run'.
ENV FLASK_APP "main.py"

RUN mkdir /app
WORKDIR /app

# Required to build the image before it is volume
# mounted.
COPY requirements.txt /app

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Allows us to use other command-line arguments
# as needed when the container image is run.
ENTRYPOINT [ "flask", "run" ]
