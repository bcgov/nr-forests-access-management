# migrations quick walkthrough

## Generate migrations from the models defined in code:

`alembic revision --autogenerate -m "migration message"`


alembic  -x tenant=fam revision -m "first migration" --autogenerate

## Generate blank migration file for future population

`alembic revision -m "migration message"`


## Run migrations

runs all the migrations defined.
```
cd api
alembic upgrade head
```

