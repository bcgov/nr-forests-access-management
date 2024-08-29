# Authorization Database Query

During the AuthN/AuthZ process, cognito will start by redirecting to single
sign on page, which will verify the identity of the request.  Cognito then
passes that information onto the lambda function that is backed by the
python code in this folder.

The python code is configured to recieve a cognito event (see
test/login_event.json for example payload), it then queries the database to
retrieve the roles for the given user, it populates the authZ information
and returns it to be signed, encoded, and returned as a JWT.

## Python Setup

We will use virtual env to isolate the python dependencies.  For local
development we will re-use / extend the virtualenv that would be setup for
backend development.  The .vscode/setting.json should already be configured
to find this config.

``` bash
cd server/auth_function
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running the tests

The tests use the testcontainer library to bring up a PostgreSQL database
during the test run. You need to have dockerd started on your computer.

```
sudo dockerd
cd server/auth_function
pytest
```
Note: We need to use master db user(postgres) to run the tests.

## Running the tests FASTER

Comment out lines 28-31 of /server/auth_function/conftest.py (the code that starts
and stops the DB container on each test run). Then you can start the fam db
container with docker compose and leave it running.

The tests expect a clean (flyway bootstrapped) database on each test run, so if
you put in your own test data or if tests fail in a weird way, you may have to
blow away the container and image and run docker compose again.

```
## Bring up the docker container permanently
docker compose up fam-flyway
```










