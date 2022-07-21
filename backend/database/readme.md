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
    --name postgres-fam \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v $POSTGRES_LOCAL_DATA_DIR:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres


```
### Test the database is working

`psql -d postgres -h 0.0.0.0 -U $POSTGRES_USER`

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


# Reverse engineer the DataModel into SQL Alchemy datamodel

```
cd database
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
sqlacodegen --schema app_fam postgresql+psycopg2://postgres:postgres@0.0.0.0/postgres  > model.py
```

the *model.py* will now contain the database model as defined in the database

Now there is a new model, the next step is to generate an alembic migration.
See ../api/alembic/readme.md for instructions on that

**note:** with the latest database migration scripts needed to upgrade
sqlacodegen.  (requirements.txt contains the latest versions)


# OLD / DEPRECATED - Run DDL output from ERStudio

```
mkdir sql
cd sql
git clone https://github.com/bcgov/nr-forests-access-management .
psql -d postgres -h 0.0.0.0 -U postgres -f db/sql/1_initial_schema.sql
rm -rf sql
```



## Flyway migrations using Docker/Podman - not working!

The most portable way to implment this is using the flyway container.  Wasn't
able to figure out how to make the flyway container to communicate with the
postgres container.

```
podman pull flyway/flyway:9.0.1
podman run flyway/flyway:9.0.1 -user=$POSTGRES_USER \
    -password=$POSTGRES_PASSWORD \
    -url=jdbc:postgresql://localhost:5432/postgres \
    migrate

# not working ^^ interpod network communication problem!  solution below does work