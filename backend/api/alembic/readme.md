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
