# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

RUN apt-get update -qq --fix-missing \
  && apt-get install -y --no-install-recommends build-essential cmake libgl1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install dlib==19.24.0
RUN pip3 install opencv-python~=4.6.0.66
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "app.py" ]
