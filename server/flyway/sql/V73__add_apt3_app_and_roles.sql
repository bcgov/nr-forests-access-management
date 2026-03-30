-- Add APT3 application and roles
-- Note, APT3 is the same as APT (or APT2) but is a modernized version (with React frontend)
--       than previous old Java-based APT applications.

-- Add APT3_DEV, APT3_TEST and APT3_PROD applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('APT3_DEV', 'Apportionment (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('APT3_TEST', 'Apportionment (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('APT3_PROD', 'Apportionment (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for APT3_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('APT_VIEWER', 'Viewer', 'Users have view-only access to content.', (select application_id from app_fam.fam_application where application_name = 'APT3_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('APT_EDITOR', 'Editor', 'Users can view and make edits to content.', (select application_id from app_fam.fam_application where application_name = 'APT3_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for APT3_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('APT_VIEWER', 'Viewer', 'Users have view-only access to content.', (select application_id from app_fam.fam_application where application_name = 'APT3_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('APT_EDITOR', 'Editor', 'Users can view and make edits to content.', (select application_id from app_fam.fam_application where application_name = 'APT3_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for APT3_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('APT_VIEWER', 'Viewer', 'Users have view-only access to content.', (select application_id from app_fam.fam_application where application_name = 'APT3_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('APT_EDITOR', 'Editor', 'Users can view and make edits to content.', (select application_id from app_fam.fam_application where application_name = 'APT3_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod Cognito app clients for APT3
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_apt3_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'APT3_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_apt3_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'APT3_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_apt3_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'APT3_PROD'), CURRENT_USER, CURRENT_DATE)
;
