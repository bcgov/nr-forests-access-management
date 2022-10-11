BEGIN;

-- Running upgrade V9 -> V10

ALTER TABLE app_fam.fam_user ALTER COLUMN user_type TYPE VARCHAR(10);

UPDATE alembic_version SET version_num='V10' WHERE alembic_version.version_num = 'V9';

COMMIT;

