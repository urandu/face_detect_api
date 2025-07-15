FROM python:3.11-slim
ENV LANG C.UTF-8

MAINTAINER bildad namawa "bildadnamawa@gmail.com"

RUN mkdir /django

COPY . /django

RUN apt-get -y update && apt-get install -y \
    python3-dev \
    build-essential \
    libmagic1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /django/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /django/requirements.txt

WORKDIR /django

EXPOSE 8000

CMD gunicorn -b :8000 face_detect_api.wsgi
