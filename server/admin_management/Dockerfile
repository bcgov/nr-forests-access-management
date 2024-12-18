FROM python:3.13

COPY requirements.txt /usr/src/
COPY api /usr/src/api

RUN cd /usr/src && pip install -r requirements.txt

ENTRYPOINT cd /usr/src && uvicorn api.app.main:app --reload --workers 1 --host 0.0.0.0 --port 8001