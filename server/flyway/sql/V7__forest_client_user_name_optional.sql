BEGIN;

-- Running upgrade V6 -> V7

ALTER TABLE app_fam.fam_forest_client ALTER COLUMN client_name DROP NOT NULL;

UPDATE alembic_version SET version_num='V7' WHERE alembic_version.version_num = 'V6';

COMMIT;

