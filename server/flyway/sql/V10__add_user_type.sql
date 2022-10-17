BEGIN;

-- Running upgrade V9 -> V10

CREATE TABLE app_fam.fam_user_type_code (
    user_type_code VARCHAR(2) NOT NULL, 
    description VARCHAR(100), 
    effective_date TIMESTAMP(6) WITHOUT TIME ZONE DEFAULT LOCALTIMESTAMP NOT NULL, 
    expiry_date TIMESTAMP(6) WITHOUT TIME ZONE, 
    update_date TIMESTAMP(6) WITHOUT TIME ZONE, 
    CONSTRAINT fam_user_type_code_pk PRIMARY KEY (user_type_code)
);

COMMENT ON TABLE app_fam.fam_user_type_code IS 'A user type is a code that is associated with the user to indicate its identity provider.';

COMMENT ON COLUMN app_fam.fam_user_type_code.user_type_code IS 'user type code';

COMMENT ON COLUMN app_fam.fam_user_type_code.description IS 'Description of what the user_type_code represents.';

COMMENT ON COLUMN app_fam.fam_user_type_code.effective_date IS 'The date and time the code was effective.';

COMMENT ON COLUMN app_fam.fam_user_type_code.expiry_date IS 'The date and time the code expired.';

COMMENT ON COLUMN app_fam.fam_user_type_code.update_date IS 'The date and time the record was created or last updated.';

ALTER TABLE app_fam.fam_user ADD COLUMN user_type_code VARCHAR(2) NOT NULL;

COMMENT ON COLUMN app_fam.fam_user.user_type_code IS 'Identifies which type of the user it belongs to; IDIR, BCeID etc.';

ALTER TABLE app_fam.fam_user DROP CONSTRAINT fam_usr_uk;

ALTER TABLE app_fam.fam_user ADD CONSTRAINT fam_usr_uk UNIQUE (user_type_code, user_name);

ALTER TABLE app_fam.fam_user ADD CONSTRAINT reffam_user_type FOREIGN KEY(user_type_code) REFERENCES app_fam.fam_user_type_code (user_type_code);

ALTER TABLE app_fam.fam_user DROP COLUMN user_type;

INSERT INTO app_fam.fam_user_type_code (user_type_code, description) VALUES ('I', 'User Type for IDIR users.');

INSERT INTO app_fam.fam_user_type_code (user_type_code, description) VALUES ('B', 'User Type for BCeID users.');

UPDATE alembic_version SET version_num='V10' WHERE alembic_version.version_num = 'V9';

COMMIT;

