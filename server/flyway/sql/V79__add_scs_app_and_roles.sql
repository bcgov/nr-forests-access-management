-- Add SCS application and roles

-- TODO: Confirm app description with the SCS team.
-- TODO: Confirm roles, role descriptions, and whether any roles are associated with forest_client.

-- Add SCS_DEV, SCS_TEST and SCS_PROD applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('SCS_DEV', 'SCS Application (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('SCS_TEST', 'SCS Application (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('SCS_PROD', 'SCS Application (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SCS_DEV
-- TODO: Update role names, display names, descriptions and role_type_code based on team confirmation.
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SCS_ADMIN', 'Admin', 'Administrative privileges for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_VIEWER', 'Viewer', 'View only privileges for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SCS_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SCS_ADMIN', 'Admin', 'Administrative privileges for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_VIEWER', 'Viewer', 'View only privileges for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SCS_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SCS_ADMIN', 'Admin', 'Administrative privileges for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_VIEWER', 'Viewer', 'View only privileges for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod Cognito app clients for SCS
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_scs_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_scs_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_scs_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), CURRENT_USER, CURRENT_DATE)
;
