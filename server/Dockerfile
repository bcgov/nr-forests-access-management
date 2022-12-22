FROM python:3.8

ENV POSTGRES_USER=fam_proxy_api
ENV POSTGRES_PASSWORD=test
ENV POSTGRES_PORT=5432
ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV POSTGRES_DB=fam
ENV POSTGRES_HOST=fam-postgres
ENV COGNITO_REGION=ca-central-1
ENV COGNITO_USER_POOL_ID=ca-central-1_5BOn4rGL8
ENV COGNITO_CLIENT_ID=26tltjjfe7ktm4bte7av998d78
ENV COGNITO_USER_POOL_DOMAIN=dev-fam-user-pool-domain

COPY ./backend/requirements.txt /usr/src/
COPY ./backend/api /usr/src/api

RUN cd /usr/src && pip install -r requirements.txt

ENTRYPOINT cd /usr/src && uvicorn api.app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000