FROM python:3.6.5-alpine3.7

# set timezone
#RUN apk --update add tzdata && \
#    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
#    apk del tzdata && \
#    rm -rf /var/cache/apk/*

ADD requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app

ENTRYPOINT ["python", "get_stage_history.py"]
