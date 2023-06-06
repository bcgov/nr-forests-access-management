# Authorization Database Query

During the AuthN/AuthZ process, cognito will start by redirecting to single
sign on page, which will verify the identity of the request.  Cognito then
passes that information onto the lambda function that is backed by the
python code in this folder.

The python code is configured to recieve a cognito event (see
test/login_event.json for example payload), it then queries the database to
retrieve the roles for the given user, it populates the authZ information
and returns it to be signed, encoded, and returned as a JWT.

## Local Development Setup

### Database Setup

You can use either the backend database docker-compose or the flyway
docker-compose to create a database that will back the development

**A) Flyway Database Setup**

``` bash
# from project root directory
# spin up a postgres database
docker-compose up

# run the flyway migrations
cd server/flyway
docker exec -it famdb flyway-migrate.sh
```

**B) Api Database Setup**

``` bash
cd server/backend
docker-compose up db
```

### Python Setup

We will use virtual env to isolate the python dependencies.  For local
development we will re-use / extend the virtualenv that would be setup for
backend development.  The .vscode/setting.json should already be configured
to find this config.

``` bash
cd server/backend
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ../auth_function
pip install -r requirements.txt
```

### Running the tests

```
cd server/auth_function
pytest
```





