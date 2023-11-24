-- -- on 'fam_application_admin' table
GRANT SELECT, UPDATE, DELETE, INSERT ON app_fam.fam_user_type_code TO ${admin_management_api_db_user}
;

ALTER TABLE app_fam.fam_application_admin
    ALTER COLUMN create_user SET DATA TYPE VARCHAR(60),
    ALTER COLUMN update_user SET DATA TYPE VARCHAR(60);
