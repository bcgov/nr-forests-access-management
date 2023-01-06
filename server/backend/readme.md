# FAM API

<img src="https://lh3.googleusercontent.com/pw/AL9nZEXIJhongvBS1KY6jUfB-SN2TxFIL0ZdoeUaByYMCgErBVCIu8tqKzEF5Ln3skKl1F7yy7o01bpNl7QqUNWtJvcSzP1BRMqQkPFqs4uyQa7BVAF8vz3RrjC72TfkISs2sycGiu6BQ2yJFmVOhrytVRU6RQ=w1592-h896-no?authuser=0" width="700">

Backend API for Forest Access Management

* [Setup / Running code locally](#setup--running)
* [Running Tests using CLI](#running-the-tests)
* [Manual update of Lambda](#manually-create-lambda-package)

# Setup / Running

## Create a virtualenv and install dependencies

```
cd server/backend

# creating venv
python3 -m venv venv

# activate venv
. ./venv/bin/activate

# install deps
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

# create env vars - make sure in the `backend` directory
# loads secrets in env-docker-compose.env to env vars
set -o allexport; source env-docker-compose.env; set +o allexport

# run the migrations
cd api
alembic upgrade head
cd ..

# activate the virtualenv if not already activated
. ./venv/bin/activate

# run the actual api
uvicorn api.app.main:app --reload
```

## potential gotchas with running the api above:

if you get this error:

```
Command 'alembic' not found, but can be installed with:

sudo apt install alembic
```

1. make sure you have [created / activated a virtualenv](#create-a-virtualenv-and-install-dependencies)
1. make sure you have installed the dev dependencies

```
sudo apt-get install -r requirements-dev.txt
```

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


# Manually create Lambda Package

When testing the lambda to save time you can manually create the package
using these commands:

```
# setup
cd server/backend
mkdir packaging
cd packaging

# get the dependencies
pip3 install -t . -r ../requirements.txt
zip -r9 ../../fam-api.zip .
cd ..

# install the actual app
cd ../../
cd server/backend
zip -u ../fam-api.zip -r api/
cd ../..
```

to verify the contents of the zip file
`unzip -l fam-api.zip`

update the zip file with only updates to api:
```
zip --delete ../fam-api.zip "api/*"
zip -u ../fam-api.zip -r api/
```


