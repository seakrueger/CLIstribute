FROM python:3.10-bookworm

ENV CONTROLLER_IP=127.0.0.1
ENV TCP_PORT=9601
ENV UDP_PORT=9602

ENV LOG_DEBUG=0
ENV CLISTRIBUTE_APT=1

ARG LOG_PATH=/var/log/clistribute

RUN apt-get update \
        && apt-get install -y --reinstall python3-apt \
        && rm -rf /var/lib/apt/lists/*
# ModuleNotFoundError: apt_pkg fix {https://stackoverflow.com/questions/13708180/python-dev-installation-error-importerror-no-module-named-apt-pkg}
RUN ln -s /usr/lib/python3/dist-packages/apt_pkg.cpython-*.so /usr/lib/python3/dist-packages/apt_pkg.so
RUN ln -s /usr/lib/python3/dist-packages/apt* /usr/local/lib/python3.10/site-packages/

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