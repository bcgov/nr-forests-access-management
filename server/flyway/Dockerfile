FROM postgres:14.4

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=test
ENV POSTGRES_PORT=5432
ENV POSTGRES_HOST_AUTH_METHOD=trust

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget -qO- https://repo1.maven.org/maven2/org/flywaydb/flyway-commandline/9.0.1/flyway-commandline-9.0.1-linux-x64.tar.gz | tar xvz && ln -s `pwd`/flyway-9.0.1/flyway /usr/local/bin
RUN chmod 775 /flyway-9.0.1/flyway

HEALTHCHECK --interval=10s --retries=3 --start-period=30s --timeout=5s \
  CMD pg_isready -U postgres

VOLUME [ "/pgdata" ]

COPY ./sql ./sql
COPY flyway-migrate.sh /usr/local/bin
RUN chmod 775 /usr/local/bin/flyway-migrate.sh
