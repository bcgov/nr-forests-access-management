BEGIN;

-- Running upgrade V17 -> V18

CREATE TABLE app_fam.fam_app_environment_type (
    app_environment_type_code VARCHAR(4) NOT NULL,
    description VARCHAR(100),
    effective_date TIMESTAMP(6) WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    expiry_date TIMESTAMP(6) WITHOUT TIME ZONE,
    update_date TIMESTAMP(6) WITHOUT TIME ZONE,
    CONSTRAINT fam_app_environment_type_pk PRIMARY KEY (app_environment_type_code)
);

COMMENT ON TABLE app_fam.fam_app_environment_type IS 'A environment type is a code that is associated with the application to indicate its nvironment.';

COMMENT ON COLUMN app_fam.fam_app_environment_type.app_environment_type_code IS 'application environment type code';

COMMENT ON COLUMN app_fam.fam_app_environment_type.description IS 'Description of what the app_environment_type_code represents.';

COMMENT ON COLUMN app_fam.fam_app_environment_type.effective_date IS 'The date and time the code was effective.';

COMMENT ON COLUMN app_fam.fam_app_environment_type.expiry_date IS 'The date and time the code expired.';

COMMENT ON COLUMN app_fam.fam_app_environment_type.update_date IS 'The date and time the record was created or last updated.';

INSERT INTO app_fam.fam_app_environment_type (app_environment_type_code, description) VALUES ('DEV', 'DEV Environment for Applicaitons.');

INSERT INTO app_fam.fam_app_environment_type (app_environment_type_code, description) VALUES ('TEST', 'TEST Environment for Applicaitons.');

INSERT INTO app_fam.fam_app_environment_type (app_environment_type_code, description) VALUES ('PROD', 'PROD Environment for Applicaitons.');

ALTER TABLE app_fam.fam_application ADD COLUMN app_environment_type_code VARCHAR(4) DEFAULT 'DEV';

COMMENT ON COLUMN app_fam.fam_application.app_environment_type_code IS 'Identifies which environment the application is for; DEV, TEST, PROD etc.';

ALTER TABLE app_fam.fam_application ADD CONSTRAINT reffam_app_env_type FOREIGN KEY(app_environment_type_code) REFERENCES app_fam.fam_app_environment_type (app_environment_type_code);

ALTER TABLE app_fam.fam_role ALTER COLUMN application_id SET NOT NULL;

ALTER TABLE app_fam.fam_role ALTER COLUMN role_purpose DROP NOT NULL;

ALTER TABLE app_fam.fam_role DROP CONSTRAINT fam_rle_name_uk;

ALTER TABLE app_fam.fam_role ADD CONSTRAINT fam_rlnm_app_uk UNIQUE (role_name, application_id);

UPDATE alembic_version SET version_num='V18' WHERE alembic_version.version_num = 'V17';

COMMIT;

