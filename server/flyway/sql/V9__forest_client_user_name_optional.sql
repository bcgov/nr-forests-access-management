BEGIN;

-- Running upgrade V8 -> V9

ALTER TABLE app_fam.fam_forest_client ALTER COLUMN client_name DROP NOT NULL;

UPDATE alembic_version SET version_num='V9' WHERE alembic_version.version_num = 'V8';

COMMIT;

