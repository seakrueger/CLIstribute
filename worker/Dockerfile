FROM python:3.10-bookworm

ENV CONTROLLER_IP=127.0.1.1
ENV LOG_DEBUG=0

ARG LOG_PATH=/var/log/clistribute

WORKDIR /clistribute

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./worker ./
COPY ./shared ./shared/

ENV CLISTRIBUTE_LOGS=${LOG_PATH}/cli-worker.log
ENV WORK_LOGS=${LOG_PATH}/work.log
RUN mkdir -p {LOG_PATH}

VOLUME [ ${LOG_PATH} ]

CMD [ "python3", "worker.py" ]