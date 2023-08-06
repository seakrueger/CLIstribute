# Webapp builder
FROM node:18-alpine AS svelte-builder

WORKDIR /client
COPY controller/ui/svelte-webapp/package*.json ./
RUN npm install 

COPY controller/ui/svelte-webapp/ ./
RUN npm run build

# Main
FROM python:3.10-bookworm

ARG PATH=/etc/clistribute
ARG LOG_PATH=${PATH}/logs
ARG DB_PATH=${PATH}/database

WORKDIR /clistribute

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./controller ./
COPY ./shared ./shared/
COPY --from=svelte-builder /client/public/build/ ./ui/svelte-webapp/public/

ENV CLISTRIBUTE_LOGS=${LOG_PATH}/cli-controller.log
ENV CLISTRIBUTE_DB=${DB_PATH}/clistribute.db
RUN mkdir -p ${PATH}/{logs,database}

EXPOSE 9600
EXPOSE 9601/tcp 9602/udp
VOLUME [ ${PATH} ]

CMD [ "python3", "main.py", "--webapp" ]