BEGIN;

-- Running upgrade V14 -> V15

GRANT SELECT, UPDATE, DELETE, INSERT
                ON ALL TABLES IN SCHEMA app_fam TO
                ${api_db_username};;

alter default privileges in schema app_fam
                  grant select, insert, delete, update
                  on tables to ${api_db_username};;

-- V12/13/14 didn't upgrade the alembic version so forcing to V15 to get
-- it back in sync
UPDATE alembic_version SET version_num='V15';
-- WHERE alembic_version.version_num = 'V14';

COMMIT;

