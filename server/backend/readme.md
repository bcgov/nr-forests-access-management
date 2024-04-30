# FAM API

Backend API for Forest Access Management

# Running the API with Docker Compose

- On the command line, go to the root of the repository
- Enter the command: `docker-compose up`

This will do three things:

1. Bring up PostgreSQL (empty) in a local docker container
2. Bring up a temporary local container that will run flyway against PostgreSQL
3. Bring up a local container with the FAM-API that connects to the local DB
4. Test the solution at <http://localhost:8000/docs>

Potential "gotchas":

- The FAM-API depends on being able to connect to the Cognito DEV environment. The values in `local-dev.env` may be out of date with the latest deployment. In particular, the values `COGNITO_USER_POOL_ID` and `COGNITO_CLIENT_ID` need to match what has been deployed by Terraform in the DEV environment. If the DEV environment gets destroyed and recreated, you have to get those two values from AWS and populate `local-dev.env` manually with the right values (and check in the change for everyone else).
- When things are running, the roles that come through in your user login will come from the AWS DEV version of the database, NOT your local database. This is because the login process is happening through Cognito, which does not know about your local environment. Don't expect local changes to be reflected in your JWT.
- There are several functions in the API that rely on the cognito username in the JWT. When developing locally and authenticating using your own IDIR, your IDIR record needs to be populated in the database so that the API can look it up. Rename sample_V1002\_\_add_local_user_cognito_id.sql and put your ACTUAL cognito username into it. Don't check it into github.
- Currently the unit tests for the API depend on connecting to the forest client API. You have to put the API key into local-dev.env in order for them to work. (Somebody please make a mock for this service!)
- Docker containers can be annoyingly "sticky". You may think you are running the latest API or flyway scripts, but an old image is still running. If you want to be sure, stop all the docker containers and remove them. Remove any API images in your local docker registry. Prune docker volumes for extra aggression! If you figure out a reliable docker-compose command to rebuild, feel free to use that instead of this super paranoid version.

# Running the API locally

These instructions assume running **without** a python virtual environment (VENV). See below for VENV considerations. If you want to be able to debug with VS Code, don't use VENV.

## Start the Database

==> **_See the Potential "gotchas" section on `Running the API with Docker Compose` first. Specific instruction is written in `.server/flyway/local_sql/sample_V1002__add_local_user_cognito_id.sql`."_**

Instruction in summary:

- Go to **".server/flyway/local_sql/"** folder.
- Rename file **sample_V1002\_\_add_local_user_cognito_id.sql** to **V1002\_\_add_local_user_cognito_id.sql**
- Open the script and find the entry corresponding to your user.
- Update the **cognito_user_id** value for your user and save the script. (If you are not sure the value, you can either get it from AWS Cognito User Pool or inspect the JWT ID Token for **"cognito:username"**)

**Note!!**: If you already had a database running initially and you adjust the `sample_V1002__add_local_user_cognito_id.sql` script to "V1002\_\_..." for your local backend database, you will need to remove the docker container and the flyway image before running docker-compose up command.

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

- `sudo apt-get install libpq-dev` -
  (was missing pg_config executable)

- `pip install wheel` -
  (needed to make this explicit)

- `sudo apt-get install python3-dev` -
  (build was failing without this, should make sure that you are running python 3.8. )

- `sudo apt-get install python3.8` -
  Make sure you are running python 3.8

- Make sure you have the correct Python interpreter selected. <Cntl><Shift><P> "Python: Select Interpreter" will give you the option if you don't want the default VENV (from settings.json). Default is VENV.

## Create or update the necessary environment variables

In general, if there is a setting change in local-dev.env, run below to have correct environments setup.

Note: This is no longer necessary if running through Docker or running tests through VS Code testrunner, as they both reference the .env file at startup.

```
cd server/backend
set -o allexport; source local-dev.env; set +o allexport
```

### Configure external services to work locally

FAM backend uses external services. These services genrally need some credentials or api tokens. The credentials or tokens should not be harcoded in "`local-dev.env`". For running backend locally or run tests locally, developers may find problem with connecting to these services. Developers can get the values and hardcode the value locally but should not commit these key values. If these are accidently commited, they should be rest.

<b>FC_API_TOKEN</b>: \
This is an API Token for Forest Client API external service to lookup forest client number organization information.

In case it needs to be reset, use [API Service Portal](https://api.gov.bc.ca/devportal/api-directory/3179?preview=false) with your IDIR credential to login and go to "Forest Client API" service to request a reset for the token.

<b>IDIM_PROXY_API_KEY</b>: \
FAM currently and temporarily has its own proxy service on Openshift (within gov network) to connect to IDIM Webservice (SOAP) to lookup user's general identity information such as IDIR (and will be for BCeID). The proxy also needs an api key.

## Run the API from VS Code launch configuration

1. Click on "Run and Debug" on the side menu bar
2. On the top of the window is a dropdown. "Debug FAM API" should be an option. Select it.
3. Click the little green arrow.

## Run the API from the command line

Depending on where python3 is installed, the command might be "python" or "python3". You WILL need the environment variables loaded in your shell session in order for this to work.

```
cd server/backend
python3 serverstart.py
```

# Using Virtual Environment

If you have multiple python projects locally and you want to isolate your FAM developments, you can use a virtual environment.

```
cd server/backend
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
python serverstart.py
```

Can use pip3 to check virtual environment dependencies version.

```
pip3 freeze
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
```

- bring up VENV environment

```
. ./venv/bin/activate
```

- run postgres tests

```
pytest
```

Potential gotchas:

- `server/backend/pytest.ini` includes some default env values but it utilizes "pytest-dotenv" to load necessary environment from local-dev.env file (see env_files: line). Some are not actually used (confirm), but need to be provided with some value for the code to run in test mode. If new tests need new environment value to be read, add it to local-dev.env should be fine (in general, keep it under one file) then if necessary, override the value in pytest.ini or config file.

## Run tests from VS Code

There is a test configuration in .vscode/launch.json. In VS Code there is a bunsen beaker icon. Clicking the icon should trigger tests discovery and from there you can use the UI.

If you created your virtualenv in the folder `backend` then the `.vscode/settings.json` should be able to find the virtualenv that you are looking for, and the tests should be configured.

If for some reason not then:

- <ctrl><shift>P
- type in `Python: Configure Tests`
- Select `Pytest`
- For Root Directory select `.`

for test Output,

- find the `output` tab
- select `Python Test Log` in from the pulldown, top right of the output window


## -------------- Windows Configuration ----------------------------------------

Before you follow the steps below, ensure you have Python installed or updated to the latest version. Install and start your Docker desktop for Windows.

```
  - cd server/backend
  - run docker compose up -d fam-flyway
  - run this command in the same directory: python3 -m venv venv
  - activate the venv environment by running this bat file: .\venv\Scripts\activate
  - Ask one of the developers for the environment properties in the local-dev.env, and update the properties in local-dev-window.env.bat with them
  - To install the required packages run: pip install -r requirements.txt
  - In the same directory, enter(run) local-dev-window.env.bat
  - To run start the backend, run python serverstart.py
```