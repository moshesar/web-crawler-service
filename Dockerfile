FROM python:latest

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt

WORKDIR /web-crawler-service