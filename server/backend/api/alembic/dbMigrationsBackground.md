# Overview

As the FAM application and database has evolved the ultimate source of truth for
the datamodel has varied.  Initially the database was defined from a bunch of
DDL output from the ER studio datamodelling tool.  Then we introduced flyway to
perform the database migrations.  Later changes to the data model were created
in the orm model (model.py), then migrations are generated from
sqlalchemy/alembic.


As development of the API has progressed it has become apparent that we needed
to have an agreement around what the source of truth is for the database.

This document describes the steps that have been taken to ultimatly harmonize
the database migrations used for development (Alembic), and the migrations that
are going to be used to deploy to AWS-RDS (flyway).  The objective of this work
is a one to one relationship between alembic->flyway migration scripts.

In some cases flyway was used to generate a database state, and alembic
migrations were reverse engineered from those changes.  The flow we are trying
to propote is alembic migrations being used to generate flyway migrations.


# Summary of work

These are the steps that were taken to create a one to one relationship between
alembic and flyway migrations.  This work has already been done and does not
need to be repeated.  I have documented it in detail here in case there is
any confusion around how this was done down the road.

**Contents:**

* [Database Setup](#database-setup)
* [Generate Alembic Migrations from Existing Flyway Migrations - V1](#generate-alembic-migrations-from-existing-flyway-migrations---v1)
* [Generate Alembic Migrations from Existing Flyway Migrations - V2](#generate-alembic-migrations-from-existing-flyway-migrations---v2)


## Database Setup

### Create a fresh Database

`docker volume rm backend_db`

### Restart the database

`cd server/backend && docker-compose up db`

### Cache or delete existing alembic migrations

Either rename or delete the directory `server/backend/api/alembic/versions`

## Generate Alembic Migrations from Existing Flyway Migrations - V1

Steps:
1. Define env vars
1. run flyway migrations on database
1. cache existing model.py
1. create a new model.py from the existing database.
1. create an alembic migration using empty database / alembic --autogenerate

### Define env vars

Either run the following command or populate the env vars below.

`set -o allexport; source server/backend/dev.env; set +o allexport`

env vars created:
* POSTGRES_USER
* POSTGRES_PASSWORD
* POSTGRES_HOST
* POSTGRES_DB
* POSTGRES_DB_TEST
* POSTGRES_PORT
* TMP_FLYWAY_DIR
* api_db_username
* api_db_password

### Run Flyway Migrations to Version 1

* assumes flyway is locally installed and configured.  [Instructions for
  installing flyway locally](./readme.md#local-flyway-install)

``` bash
flyway -user=$POSTGRES_USER \
    -password=$POSTGRES_PASSWORD \
    -url=jdbc:postgresql://localhost:5432/postgres \
    -locations=filesystem:$TMP_FLYWAY_DIR \
    -placeholders.api_db_username=fam_proxy_api \
    -placeholders.api_db_password=fam_proxy_api \
    -target=1 \
    migrate
```

### Run sqlacodegen to generate the orm model (model.py) - done2

* Assumes you have created a virtualenv and have installed the dev requirements
    installed - [instructions](../../readme.md#install-dependencies)

`sqlacodegen --schema app_fam postgresql+psycopg2://postgres:postgres@0.0.0.0/postgres  > server/backend/api/app/models/model.py`

Then add the following line to the model.py after the line:

``` python
Base = declarative_base()
# insert metadata line after ^^ that line.
metadata = Base.metadata
```

### Generate alembic migration

* the following code will look at the state of the current database vs the sqlalchemy
   ORM model, calculate the differences, and generate an alembic migration based
   on the differences.

`cd server/backend/api && alembic revision --autogenerate -m "initial schema" && cd ../../..`

If all went well you should now have a new alembic migration file:
[server/backend/api/alembic/versions/V1_initial_schema.py](server/backend/api/alembic/versions/V1_initial_schema.py)

You now need to manually tweak the migration file to tell it to use the app_fam schema:

* add to first line for upgrade:     `op.execute("create schema app_fam")`
* add to last line for downgrade:     `op.execute("drop schema app_fam")`

### Execute the alembic Migration

* At this stage the alembic migration should only generate the alembic version
  table that it uses to keep track of what migrations have and have not been run.

`cd server/backend/api && alembic upgrade V1 && cd ../../../`


## Generate Alembic Migrations from Existing Flyway Migrations - V2

### Upgrade database to V2 using flyway

```
flyway -user=$POSTGRES_USER \
    -password=$POSTGRES_PASSWORD \
    -url=jdbc:postgresql://localhost:5432/postgres \
    -locations=filesystem:$TMP_FLYWAY_DIR \
    -placeholders.api_db_username=fam_proxy_api \
    -placeholders.api_db_password=fam_proxy_api \
    -target=2 \
    migrate
```

**note:** target is set to `2` which corresponds to the version number of the
flyway migration

### Create an empty alembic migration

`cd server/backend/api && alembic revision -m "initial schema" && cd ../../..`

then verify that the file: [server/backend/api/alembic/versions/V2_first_application.py](server/backend/api/alembic/versions/V2_first_application.py) has been generated.

### Manually edit alembic migration

The V2 flyway migration only adds two rows to the database.  To ensure the
dev env and the production env are the same we want to have this data inlcuded
in an alembic migration.

start by adding the following import to the imports section of migration file:

```python
import app.models.model
```

then add the following lines to the `upgrade()` method in order to insert the
required application records:

``` python
    famApp = app.models.model.FamApplication.__table__
    op.bulk_insert(famApp,
        [
            {'application_name': 'fam',
            'application_description': 'Forests Access Management',
            'create_user': 'fam_proxy_api',
            'update_user': 'fam_proxy_api'
            },
            {'application_name': 'fom',
            'application_description': 'Forest Operations Map',
            'create_user': 'fam_proxy_api',
            'update_user': 'fam_proxy_api'
            }
        ]
    )
```

### Run the alembic Migration

Even though the data already exists from the flyway migration, running the
alembic migration ensures that the alembic version table is updated.

`cd server/backend/api && alembic upgrade V2 && cd ../../..`

### Merge the orm model changes

Do a diff of the original model.py from the dev branch of the repo against the
current model.py, and pull in any changes.

I ended up pulling in almost all the changes so you could also at this stage just
replace the original model.py with the one from the dev branch.

## Create V3 Alembic / Flyway Migration

### Create Alembic Migration File

Went back into the git/dev branch and grabbed the `server/backend/api/alembic/versions/1b5a533f281f_columns_to_nullable_for_fam_role_table.py` file and renamed in current
branch to be `V3_allow_role_appid_not_null.py`

### Create the corresponding flyway migration file

Run the command:
`cd server/backend/alembic && python3 generateFlywayMigrations.py && cd ../../..`

Then edit the newly generated flyway migration file by adding the sql to create
an alembic migration table (server/flyway/sql/V3__allow_role_appid_not_null.sql)

```sql
CREATE TABLE IF NOT EXISTS alembic_version
(
    version_num character varying(32),
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
```

## Create V4 Alembic / Flyway Migration

went back into git/dev branch and grabbed the `server/backend/api/alembic/versions/e579238143a5_date_column_localtimestamp_as_default.py` file and renamed to current branch as `V4_date_column_localtimestamp_as_default.py`

### Create the corresponding flyway migration file

Run the command:
`cd server/backend/alembic && python3 generateFlywayMigrations.py && cd ../../..`

## Create V5 Alembic / Flyway Migration

This step is mostly cleanup.  Original column comments included trailing spaces.
At some point either in the model generation or the alembic migrations the
spaces got removed.  This final migration ensures that the dev db is identifical
to the db that is going to be implemented.

### Generate the alembic migration

`cd server/backend/api && alembic revision --autogenerate -m "post alembic migrations" && cd ../../..`

### Run all the alembic migrations

`cd server/backend/api && alembic upgrade V5 && cd ../../..`

### Generate the flyway migrations

`cd server/backend/api/alembic && python generateFlywayMigrations.py & cd ../../../..`

