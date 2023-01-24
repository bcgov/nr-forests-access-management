BEGIN;

-- Running upgrade V17 -> V18

CREATE TABLE app_fam.fam_app_environment (
    app_environment VARCHAR(4) NOT NULL,
    description VARCHAR(100),
    effective_date TIMESTAMP(6) WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    expiry_date TIMESTAMP(6) WITHOUT TIME ZONE,
    update_date TIMESTAMP(6) WITHOUT TIME ZONE,
    CONSTRAINT fam_app_environment_pk PRIMARY KEY (app_environment)
);

COMMENT ON TABLE app_fam.fam_app_environment IS 'Used by the application to indicate its environment.';

COMMENT ON COLUMN app_fam.fam_app_environment.app_environment IS 'Application environment.';

COMMENT ON COLUMN app_fam.fam_app_environment.description IS 'Description of what the app_environmentrepresents.';

COMMENT ON COLUMN app_fam.fam_app_environment.effective_date IS 'The date and time the record was effective.';

COMMENT ON COLUMN app_fam.fam_app_environment.expiry_date IS 'The date and time the record expired.';

COMMENT ON COLUMN app_fam.fam_app_environment.update_date IS 'The date and time the record was created or last updated.';

INSERT INTO app_fam.fam_app_environment (app_environment, description) VALUES ('DEV', 'DEV Environment for Applicaitons.');

INSERT INTO app_fam.fam_app_environment (app_environment, description) VALUES ('TEST', 'TEST Environment for Applicaitons.');

INSERT INTO app_fam.fam_app_environment (app_environment, description) VALUES ('PROD', 'PROD Environment for Applicaitons.');

ALTER TABLE app_fam.fam_application ADD COLUMN app_environment VARCHAR(4);

COMMENT ON COLUMN app_fam.fam_application.app_environment IS 'Identifies which environment the application is for; DEV, TEST, PROD etc.';

ALTER TABLE app_fam.fam_application ADD CONSTRAINT reffam_app_env FOREIGN KEY(app_environment) REFERENCES app_fam.fam_app_environment (app_environment);

ALTER TABLE app_fam.fam_role ALTER COLUMN application_id SET NOT NULL;

ALTER TABLE app_fam.fam_role ALTER COLUMN role_purpose DROP NOT NULL;

ALTER TABLE app_fam.fam_role DROP CONSTRAINT fam_rle_name_uk;

ALTER TABLE app_fam.fam_role ADD CONSTRAINT fam_rlnm_app_uk UNIQUE (role_name, application_id);

UPDATE alembic_version SET version_num='V18' WHERE alembic_version.version_num = 'V17';

COMMIT;

