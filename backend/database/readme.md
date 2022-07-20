# Description

Work / files related to creating a temporary database using docker,
loading the ddl defined for FAM, then using the database structure to
generate a sqlalchmey data model.

Investigate reverse engineering the datamodel into fastapi.

# Run Database in a container

create the following env vars:
* POSTGRES_PASSWORD - Database password
* POSTGRES_USER  - Database user
* POSTGRES_LOCAL_DATA_DIR - directory on my machine where postgres will persist its
    data.

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

 psql -d postgres -h 0.0.0.0 -U postgres
```

# Run DDL output from ERStudio

```
mkdir sql
cd sql
git clone https://github.com/bcgov/nr-forests-access-management .
psql -d postgres -h 0.0.0.0 -U postgres -f db/sql/1_initial_schema.sql
rm -rf sql
```

    flyway -user=myuser -password=s3cr3t -url=jdbc:h2:mem -placeholders.abc=def migrate
    jdbc:postgresql://0.0.0.0:5432/postgres

# Run flyway migrations
```
podman pull flyway/flyway:9.0.1
podman run flyway/flyway:9.0.1 -user=$POSTGRES_USER \
    -password=$POSTGRES_PASSWORD \
    -url=jdbc:postgresql://localhost:5432/postgres \
    migrate

# not working ^^ interpod network communication problem!  solution below does work through.

# Install flyway locally:
wget -qO- https://repo1.maven.org/maven2/org/flywaydb/flyway-commandline/9.0.1/flyway-commandline-9.0.1-linux-x64.tar.gz | tar xvz && sudo ln -s `pwd`/flyway-9.0.1/flyway /usr/local/bin

flyway -user=$POSTGRES_USER \
    -password=$POSTGRES_PASSWORD \
    -url=jdbc:postgresql://localhost:5432/postgres \
    migrate
```

# reverse engineer the DataModel into SQL Alchemy datamodel

```
cd database
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
python -m sqlacodegen postgresql+psycopg2://postgres:postgres@0.0.0.0/postgres > model.py
```

the *model.py* will now contain the database model as defined in the database

Now there is a new model, the next step is to generate an alembic migration.
See ../api/alembic/readme.md for instructions on that
