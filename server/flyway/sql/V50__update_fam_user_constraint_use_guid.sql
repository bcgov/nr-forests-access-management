-- Update unique constraint in fam user table to be user type code and user guid

DROP INDEX app_fam.fam_usr_uk;

CREATE UNIQUE INDEX fam_usr_uk ON app_fam.fam_user(user_type_code, lower(user_guid));