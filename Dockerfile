FROM debian:stretch-slim

LABEL maintainer="aospan@jokersys.com"

RUN apt-get update && apt-get install -y \
    vim python python-pip && pip install influxdb tox

COPY get_miner_stats.py /

#don't forget to define env variables:
# MINER_HOST=192.168.1.99
# MINER_DB_HOST=localhost
CMD python /get_miner_stats.py
