BEGIN;

-- Running upgrade V5 -> V6

CREATE TABLE app_fam.fam_role_type (
    role_type_code VARCHAR(2), 
    description VARCHAR(100), 
    effective_date TIMESTAMP(6) WITHOUT TIME ZONE NOT NULL, 
    expiry_date TIMESTAMP(6) WITHOUT TIME ZONE, 
    update_date TIMESTAMP(6) WITHOUT TIME ZONE, 
    CONSTRAINT fam_role_type_code_pk PRIMARY KEY (role_type_code), 
    CHECK (role_type_code IN ('C', 'A'))
);

COMMENT ON TABLE app_fam.fam_role_type IS 'A role type is a code that is associated with roles that will influence what can be associate with a role.  At time of implementation an abstract role can only have other roles related to it, while a concrete role can only have users associated with it';

COMMENT ON COLUMN app_fam.fam_role_type.role_type_code IS 'role type code';

COMMENT ON COLUMN app_fam.fam_role_type.description IS 'Description of what the role_type_code represents';

COMMENT ON COLUMN app_fam.fam_role_type.effective_date IS 'The date and time the code was effective.';

COMMENT ON COLUMN app_fam.fam_role_type.expiry_date IS 'The date and time the code expired.';

COMMENT ON COLUMN app_fam.fam_role_type.update_date IS 'The date and time the record was created or last updated.';

ALTER TABLE app_fam.fam_role ADD COLUMN role_type_code VARCHAR(2) NOT NULL;

COMMENT ON COLUMN app_fam.fam_role.role_type_code IS 'Identifies if the role is an abstract or concrete role. Users should only be assigned to roles where role_type=concrete';

ALTER TABLE app_fam.fam_role ADD CONSTRAINT reffam_role_type FOREIGN KEY(role_type_code) REFERENCES app_fam.fam_role_type (role_type_code);

INSERT INTO app_fam.fam_role_type (role_type_code, description, effective_date, update_date) VALUES ('A', 'Abstract role, can only be associated with other roles', '2022-09-27 18:49:18', '2022-09-27 18:49:18');

INSERT INTO app_fam.fam_role_type (role_type_code, description, effective_date, update_date) VALUES ('C', 'Concrete Role, can only be associated with other users', '2022-09-27 18:49:18', '2022-09-27 18:49:18');

UPDATE alembic_version SET version_num='V6' WHERE alembic_version.version_num = 'V5';

COMMIT;

