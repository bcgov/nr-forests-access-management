BEGIN;

-- Running upgrade V7 -> V8

ALTER TABLE app_fam.fam_user ALTER COLUMN user_type TYPE VARCHAR(10);

UPDATE alembic_version SET version_num='V8' WHERE alembic_version.version_num = 'V7';

COMMIT;

