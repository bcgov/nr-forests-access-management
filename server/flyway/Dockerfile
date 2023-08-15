FROM flyway/flyway:latest

# RUN mkdir sql

COPY ./sql sql
COPY ./local_sql sql

CMD ["info", "migrate", "info"]
