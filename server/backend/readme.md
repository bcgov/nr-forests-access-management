# FAM API

Backend API for Forest Access Management

# Setup / Running

## install dependencies

```
cd server/backend
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

install the development dependencies (linter/formatters/utilities/etc)

```
pip install -r requirements-dev.txt
```
### potential gotchas running pip install above:

sudo apt-get install libpq-dev
(was missing pg_config executable)

pip install wheel
(needed to make this explicit)

sudo apt-get install python3-dev
(build was failing without this)

## run the api - locally for development

```
cd server/backend

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

## potential gotchas with running the api above:

sudo apt-get install alembic
(needed to install the executable)

# Running the tests

instructions here are for running tests in vscode, you can also run them manually on the
the command line.  Tests use the [pytest](https://docs.pytest.org/en/7.1.x/) testing framework

## Tell VS Code what framework to use

If you created your virtualenv in the folder `backend` then the
.vscode/settings.json should be able to find the virtualenv that you are looking
for, and the tests should be configured.

If for some reason not then:
* <ctrl><shift>P
* type in `Python: Configure Tests`
* Select `Pytest`
* For Root Directory select `.`

for test Output,
* find the `output` tab
* select `Python Test Log` in from the pulldown, top right of the output window
