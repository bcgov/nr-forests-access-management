BEGIN;

-- Running upgrade V3 -> V4

ALTER TABLE app_fam.fam_application ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_application ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_forest_client ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_forest_client ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_user ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_user ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_application_client ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_application_client ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_group ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_group ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_role ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_role ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_application_group_xref ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_application_group_xref ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_group_role_xref ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_group_role_xref ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_user_group_xref ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_user_group_xref ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_user_role_xref ALTER COLUMN create_date SET DEFAULT LOCALTIMESTAMP;

ALTER TABLE app_fam.fam_user_role_xref ALTER COLUMN update_date SET DEFAULT LOCALTIMESTAMP;

UPDATE alembic_version SET version_num='V4' WHERE alembic_version.version_num = 'V3';

COMMIT;

