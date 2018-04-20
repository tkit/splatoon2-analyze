FROM python:3.6.5-alpine3.7

ADD requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
ENTRYPOINT ["python", "get_league_ranking.py"]
