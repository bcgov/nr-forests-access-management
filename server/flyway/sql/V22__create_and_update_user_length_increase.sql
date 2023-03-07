-- Running upgrade V21 -> V22

-- Increase create_user and update_user to (60)

ALTER TABLE app_fam.fam_application
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_application_client
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_application_group_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_forest_client
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_group
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_group_role_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_role
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_user
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_user_group_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);

ALTER TABLE app_fam.fam_user_role_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);
