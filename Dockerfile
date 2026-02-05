FROM python:3.11-slim

RUN mkdir -p /home/agent/docs
COPY files/docs/ /home/agent/docs/

WORKDIR /home/agent
