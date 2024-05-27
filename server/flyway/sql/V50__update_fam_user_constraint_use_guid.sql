ALTER TABLE app_fam.fam_user DROP CONSTRAINT fam_usr_uk;

CREATE UNIQUE INDEX fam_usr_uk ON app_fam.fam_user(user_type_code, lower(user_guid));