BEGIN;

-- Running upgrade V15 -> V16

ALTER TABLE app_fam.fam_forest_client DROP CONSTRAINT fam_for_cli_name_uk;

DROP INDEX app_fam.ix_app_fam_fam_forest_client_client_name;

ALTER TABLE app_fam.fam_forest_client DROP COLUMN client_name;

UPDATE alembic_version SET version_num='V16' WHERE alembic_version.version_num = 'V15';

COMMIT;

