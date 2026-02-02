FROM python:3.11-slim

RUN mkdir -p /home/agent/docs
COPY files/docs/system_requirements.txt /home/agent/docs/
COPY files/docs/api_reference.txt /home/agent/docs/
COPY files/docs/README.txt /home/agent/docs/

WORKDIR /home/agent
