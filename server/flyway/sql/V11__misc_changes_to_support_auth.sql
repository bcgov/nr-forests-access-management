BEGIN;

-- Running upgrade V10 -> V11

ALTER TABLE app_fam.fam_application_client ALTER COLUMN update_date TYPE TIMESTAMP(6) WITHOUT TIME ZONE USING update_date::timestamp(6) without time zone;

ALTER TABLE app_fam.fam_application_client ALTER COLUMN update_date SET NOT NULL;

COMMENT ON COLUMN app_fam.fam_application_client.update_date IS 'The date and time the record was created.';

ALTER TABLE app_fam.fam_application_client ADD CONSTRAINT cognito_app_uk UNIQUE (cognito_client_id, application_id);

ALTER TABLE app_fam.fam_user ALTER COLUMN cognito_user_id TYPE VARCHAR(100);

UPDATE alembic_version SET version_num='V11' WHERE alembic_version.version_num = 'V10';

COMMIT;

