FROM python:3.8

ENV POSTGRES_USER=fam_proxy_api
ENV POSTGRES_PASSWORD=test
ENV POSTGRES_PORT=5432
ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV POSTGRES_DB=fam
ENV POSTGRES_HOST=fam-postgres

COPY ./backend /usr/src/

RUN cd /usr/src && pip install -r requirements.txt

ENTRYPOINT cd /usr/src && uvicorn api.app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000