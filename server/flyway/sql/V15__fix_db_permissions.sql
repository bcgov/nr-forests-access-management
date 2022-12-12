BEGIN;

-- Running upgrade V14 -> V15

GRANT SELECT, UPDATE, DELETE, INSERT
                ON ALL TABLES IN SCHEMA app_fam TO
                fam_proxy_api;

-- V12/13/14 didn't upgrade the alembic version so forcing to V15 to get it back
-- in sync
UPDATE alembic_version SET version_num='V15'
--WHERE alembic_version.version_num = 'V14';

COMMIT;

