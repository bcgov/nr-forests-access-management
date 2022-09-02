# Description

Work related to running flyway migrations locally to a temporary containerized
database, and then using [sqlacodegen](https://pypi.org/project/sqlacodegen/) to
create a new sqlalchemy model.

# Run Database in a container

### Create the following env vars:

* POSTGRES_PASSWORD - Database password
* POSTGRES_USER  - Database user
* POSTGRES_LOCAL_DATA_DIR - directory on my machine where postgres will persist its
    data.

### use Docker/Podman to create a temporary database instance
```
podman pull postgres

mkdir $POSTGRES_LOCAL_DATA_DIR

podman run -d \
    --name fam \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v $POSTGRES_LOCAL_DATA_DIR:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres

```
### Test the database is working

`psql -d postgres -h 0.0.0.0 -U $POSTGRES_USER`

quit...  `\q`

# Run flyway migrations

The flyway migrations are run by terraform, which injects in variables into the
sql, the variable injection doesn't work when run the scripts through command
line flyway.

The current solution is running a bash script that generates temporary versions
of the sql, with variables being dereferenced.

## Get flyway commandline

flyway can be downloaded from: https://flywaydb.org/download/community


### Get the flyway cli for linux / wsl

```
wget -qO- https://repo1.maven.org/maven2/org/flywaydb/flyway-commandline/9.0.1/flyway-commandline-9.0.1-linux-x64.tar.gz | tar xvz && sudo ln -s `pwd`/flyway-9.0.1/flyway /usr/local/bin`
```

### Running flyway migrations

Due to injected variables in the sql migration files, recommend the best way to
run the migration is to use the `runmigratons.sh` shell script.

`bash runmigratons.sh`

### Run up to a specific versions

flyway -user=$POSTGRES_USER \
    -password=$POSTGRES_PASSWORD \
    -url=jdbc:postgresql://localhost:5432/postgres \
    -locations=filesystem:$TMP_FLYWAY_DIR \
    -placeholders.api_db_username=fam_proxy_api \
    -placeholders.api_db_password=fam_proxy_api \
    -target=2 \
    migrate


# Reverse engineer the DataModel into SQL Alchemy datamodel

* make sure the virtualenv is invoked
* if you haven't installed the dev dependencies do so now

`cd backend && pip install -r requirements-dev.txt`

now, generate a new model based on what exists in the database...

```
cd database
sqlacodegen --schema app_fam postgresql+psycopg2://postgres:postgres@0.0.0.0/postgres  > /home/kjnether/proj/fam-api/server/backend/api/app/models/model.py
```

the *model.py* will now contain the database model as defined in the database.
the next steps:

1. shutdown the temporary database and delete the folder
    `sudo rm -rf $POSTGRES_LOCAL_DATA_DIR`
1. spin up the old database using docker-compose
    `dc up db`
1. replace  backend/api/app/models/model.py with the new model.py
1. use alembic to generate a new alembic migration
    `alembic revision --autogenerate -m "initial schema"`

    ```




**note:** with the latest database migration scripts needed to upgrade
sqlacodegen.  (requirements.txt contains the latest versions)

