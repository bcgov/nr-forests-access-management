# FAM API

Backend API for Forest Access Management

# Running the API with Docker Compose

* On the command line, go to the root of the repository
* Enter the command: `docker-compose up`

This will do three things:

1. Bring up PostgreSQL (empty) in a local docker container
2. Bring up a temporary local container that will run flyway against PostgreSQL
3. Bring up a local container with the FAM-API that connects to the local DB
4. Test the solution at <http://localhost:8000/docs>

Potential "gotchas":

* The FAM-API depends on being able to connect to the Cognito DEV environment. The values in `local-dev.env` may be out of date with the latest deployment. In particular, the values `COGNITO_USER_POOL_ID` and`COGNITO_CLIENT_ID` need to match what has been deployed by Terraform in the DEV environment. If the DEV environment gets destroyed and recreated, you have to get those two values from AWS and populate `local-dev.env` manually with the right values (and check in the change for everyone else).
* When things are running, the roles that come through in your user login will come from the AWS DEV version of the database, NOT your local database. This is because the login process is happening through Cognito, which does not know about your local environment. Don't expect local changes to be reflected in your JWT.
* Docker containers can be annoyingly "sticky". You may think you are running the latest API or flyway scripts, but an old image is still running. If you want to be sure, stop all the docker containers and remove them. Remove any API images in your local docker registry. Prune docker volumes for extra aggression! If you figure out a reliable docker-compose command to rebuild, feel free to use that instead of this super paranoid version.

# Running the API locally

These instructions assume running **without** a python virtual environment (VENV). See below for VENV considerations. If you want to be able to debug with VS Code, don't use VENV.

## Start the Database

When running the API locally, you still need to have a working database to connect to. Docker compose can run everything **other than the API** with the command:

`docker-compose fam-flyway up`

This command will run the services in the Docker Compose definition but will omit the API.

## Install all the necessary Python libraries

Assuming you have Python3 installed locally (or are running VENV with Python3 installed):

```
cd server/backend
pip install -r requirements.txt
```

Potential gotchas (developer notes -- may not need!):

* `sudo apt-get install libpq-dev` -
    (was missing pg_config executable)

* `pip install wheel` -
    (needed to make this explicit)

* `sudo apt-get install python3-dev` -
    (build was failing without this, should make sure that you are running python 3.8. )

* `sudo apt-get install python3.8` -
    Make sure you are running python 3.8

## Create or update the necessary environment variables

```
cd server/backend
set -o allexport; source local-dev.env; set +o allexport
```

## Run the API from the command line

Depending on where python3 is installed, the command might be "python" or "python3"

```
cd server/backend
python3 serverstart.py
```

## Alternatively, run the API from VS Code in debug mode

1. Open `serverstart.py` in VS Code
2. Click "Run and Debug" on the VS Code toolbar (or use Ctrl+Shift+D)
3. Click "Run and Debug" button
4. Select "Debug the currently active Python file"

## Alternatively, run the API from VS Code launch configuration

1. Click on "Run and Debug" on the side menu bar
2. On the top of the window is a dropdown. "Debug FAM API" should be an option. Select it.
3. Click the little green arrow.

The debug configuration is in /.vscode/launch.json. The environment variable get loaded at runtime from the local-dev.env file.

# Using Virtual Environment

If you have multiple python projects locally and you want to isolate your FAM developments, you can use a virtual environment. VS Code does not debug into the virtual environment (that we can determine).

```
cd server/backend
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
python serverstart.py
```

# Running the tests

Tests are running using pytest. They can be run from the command line or using VS Code tools.
Test sets are located under "server/backend/testspg", it contains unit tests and integration tests that uses "testcontainers" to spin up a temporary "Postgres" database container. Pytest config will connect to the temporary database container for testing.

## Install test dependencies

Assuming you've already installed the dependencies from requirements.txt, you just need to install the dependencies from requirements-dev.txt. If you are running in a VENV, make sure you run the install command in the same VENV.

```
cd server/backend
pip install -r requirements-dev.txt
```

## Run tests from the command line

```
cd server/backend

# bring up VENV environment
. ./venv/bin/activate

# run postgres tests
pytest

Potential gotchas:

* `server/backend/pytest.ini` includes some default env values but it utilizes "pytest-dotenv" to load necessary environment from local-dev.env file (see env_files: line). Some are not actually used (confirm), but need to be provided with some value for the code to run in test mode. If new tests need new environment value to be read, add it to local-dev.env should be fine (in general, keep it under one file) then if necessary, override the value in pytest.ini or config file.

## Run tests from VS Code

Some developers run tests from VS Code. This author (Conrad) has never gotten the VS Code configuration correct, so YMMV. Notes from previous developer (please fix if you verify that it works for you!). If it's working, you can go to the "Testing" icon on the VS Code menu (looks like a test tube) and VS Code should discover all the tests for you.

Kevin had it working by running VENV and pointing to it from `.vscode/settings.json` (which controls the VS Code behaviour).

If you created your virtualenv in the folder `backend` then the `.vscode/settings.json` should be able to find the virtualenv that you are looking for, and the tests should be configured.

If for some reason not then:
* <ctrl><shift>P
* type in `Python: Configure Tests`
* Select `Pytest`
* For Root Directory select `.`

for test Output,
* find the `output` tab
* select `Python Test Log` in from the pulldown, top right of the output window




