FROM python:3.11-slim

RUN mkdir -p /home/agent/

COPY files/docs/ei.txt /home/agent/
COPY files/docs/memo-260108.txt /home/agent/
COPY files/docs/memo-260113.txt /home/agent/
#COPY files/docs/system_requirements.txt /home/agent/
COPY files/docs/deployment.log /home/agent


WORKDIR /home/agent
