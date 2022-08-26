# Generate a new alembic migration based on changes to the model.py

This is what needs to be run after `sqlacodegen` has been used to
reverse engineer the database into an ORM

`alembic revision --autogenerate -m "migration message"`

## Generate blank migration file for future population

`alembic revision -m "migration message"`


## Run migrations

Having generated a new alembic migration, you can then apply it:
```
cd api
alembic upgrade head
```

## Generate a new flyway migration

1. Address Latest ER Studio migration

* a new migration exists that was created by Richard, in PR: https://github.com/bcgov/nr-forests-access-management/pull/100
* That migration hasn't been run.
* are we going to run into more of these?
    * if so need to regenerate the model.py, and then merge the differences in
      order to capture the changes that Ian has created.

    * discussed with Ian, changes were encorporated into the orm migrations


2. Need to build relationship between alembic migrations / flyway migrations
   in order to determine if a new flyway migration needs to be generated.

   * how to do this:
      * naming convension?
        - looking into whether we can add something to get the alembic migrations
          to be named using the same pattern as flyway expects
            * Working on now!

      * modified the env.py and the alembic.ini to generate migration revision
        ids named V1... V2 etc.  Now the migration names of the alembic migrations
        can be related to the flyway migrations

      * Alembic, like flyway has a version table that it creates in the database
        to keep track of what migrations have been run and which have not.
        The existing flyway migrations will not contain this table as they were
        generated from ER-studio.

    manual generation of alembic to flyway migrations:

    Create sql for everything up to V2:
      `alembic upgrade V2 --sql > junk.sql`

    Create sql for only V2
     `alembic upgrade V1:V2 --sql > junk.sql`




