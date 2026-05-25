-- Add FREP application and roles
-- Add FREP_DEV, FREP_TEST and FREP_PROD applications

INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('FREP_DEV', 'Forest and Range Evaluation Program (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('FREP_TEST', 'Forest and Range Evaluation Program (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('FREP_PROD', 'Forest and Range Evaluation Program (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for FREP_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('FREP_ADMIN', 'Administrator', 'Add, edit, delete, and view FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('FREP_EDITOR', 'Decision Maker', 'Edit FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('FREP_VIEW_ONLY', 'View Only', 'View only access to FREP application.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ;

-- Add roles for FREP_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('FREP_ADMIN', 'Administrator', 'Add, edit, delete, and view FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('FREP_EDITOR', 'Decision Maker', 'Edit FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('FREP_VIEW_ONLY', 'View Only', 'View only access to FREP application.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
;

-- Add roles for FREP_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('FREP_ADMIN', 'Administrator', 'Add, edit, delete, and view FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('FREP_EDITOR', 'Decision Maker', 'Edit FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('FREP_VIEW_ONLY', 'View Only', 'View only access to FREP application.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
;

-- Create dev, test and prod Cognito app clients for FREP
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_frep_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_frep_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_frep_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), CURRENT_USER, CURRENT_DATE)
;
