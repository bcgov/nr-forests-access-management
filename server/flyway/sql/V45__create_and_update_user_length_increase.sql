-- Increase create_user and update_user to (100) because business bceid user's cognito_user_id is longer than 60 chars

ALTER TABLE app_fam.fam_application
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_application_client
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_application_group_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_forest_client
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_group
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_group_role_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_role
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_user
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_user_group_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_user_role_xref
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_access_control_privilege
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);

ALTER TABLE app_fam.fam_application_admin
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(100),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(100);