FROM python:3.9-alpine
WORKDIR /app

COPY requirements.txt /requirements.txt
RUN pip install --user -r /requirements.txt

COPY zuvio.py /app
COPY config.json /app

ENV USER=user,
ENV PASSWD=password
ENV LINE_NOTIFY_TOKEN=lineNotifyToken
ENV LAT=24.122438
ENV LNG=120.650394
ENV WAITSEC=10
ENV FULLMODE=1
ENV LINE_NOTIFY_ON=1
ENV LOOP_ON=1
ENV WAIT_SEC_AFTER_CALL=60

CMD [ "python", "zuvio.py" ]