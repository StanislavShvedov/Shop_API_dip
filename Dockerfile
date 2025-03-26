FROM python:3.11.8-slim-bookworm
RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev --no-install-recommends


COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /shop_API_service
WORKDIR /shop_API_service

