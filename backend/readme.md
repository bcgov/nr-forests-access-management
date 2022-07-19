# FAM API

Backend API for Forest Access Management

# Setup / Running

## install dependencies

```
cd backend
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

## run the api - locally for development

```
cd backend

# run the backend postgres db
docker-compose up db

# run the migrations
cd api
alembic upgrade head
cd ..

# create env vars - make sure in the `backend` directory
# loads secrets in env-db-dev.env to env vars
set -o allexport; source env-db-dev.env; set +o allexport

# activate the virtualenv if not already activated
. ./venv/bin/activate

# run the actual api
uvicorn api.app.main:app --reload
```