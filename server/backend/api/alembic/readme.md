# Migrations - How to

1. make changes in model.py





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


## reset database:

Find the database volume:
`docker volume ls`

Delete the database volume
`docker volume rm backend_db`

if error like this shows up:
`Error response from daemon: remove backend_db: volume is in use - [1e14af6c71d6c803a27e32525b43c0bc3f360a8ca176473461ca938f6b66ada2]`

then stop and remove the container and then delete the volume:

```
docker container stop <container id>
docker container rm <container id>
docker volume rm backend_db
```

## Manually generate a flyway migration from alembic migration

Create sql for everything up to V2:

`alembic upgrade V2 --sql > {flyway migration file}`

Create sql for only V2:

`alembic upgrade V1:V2 --sql > {flyway migration file}`

Get alembic history

`alembic history`
