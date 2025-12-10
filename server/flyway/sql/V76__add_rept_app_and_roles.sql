-- Add REPT application and roles

-- Add REPT_DEV, REPT_TEST and REPT_PROD applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('REPT_DEV', 'Reporting (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('REPT_TEST', 'Reporting (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('REPT_PROD', 'Reporting (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for REPT_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('REPT_ADMIN', 'Admin', 'Full administrative privileges across the REPT application — create/read/update/delete projects and reports, trigger and download Jasper reports, manage application settings, and perform administrative user operations.', (select application_id from app_fam.fam_application where application_name = 'REPT_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('REPT_VIEWER', 'Viewer', 'View only privileges across the REPT application — read projects and reports, trigger and download Jasper reports.', (select application_id from app_fam.fam_application where application_name = 'REPT_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for REPT_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('REPT_ADMIN', 'Admin', 'Full administrative privileges across the REPT application — create/read/update/delete projects and reports, trigger and download Jasper reports, manage application settings, and perform administrative user operations.', (select application_id from app_fam.fam_application where application_name = 'REPT_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('REPT_VIEWER', 'Viewer', 'View only privileges across the REPT application — read projects and reports, trigger and download Jasper reports.', (select application_id from app_fam.fam_application where application_name = 'REPT_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for REPT_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('REPT_ADMIN', 'Admin', 'Full administrative privileges across the REPT application — create/read/update/delete projects and reports, trigger and download Jasper reports, manage application settings, and perform administrative user operations.', (select application_id from app_fam.fam_application where application_name = 'REPT_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('REPT_VIEWER', 'Viewer', 'View only privileges across the REPT application — read projects and reports, trigger and download Jasper reports.', (select application_id from app_fam.fam_application where application_name = 'REPT_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod Cognito app clients for REPT
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_rept_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'REPT_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_rept_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'REPT_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_rept_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'REPT_PROD'), CURRENT_USER, CURRENT_DATE)
;
