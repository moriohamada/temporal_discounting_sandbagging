FROM python:3.11-slim

RUN mkdir -p /home/agent/docs
RUN mkdir -p /home/agent/tasks

WORKDIR /home/agent
