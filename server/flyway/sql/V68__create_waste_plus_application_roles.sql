-- Create WASTE PLUS applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('WASTE_PLUS_DEV', 'Waste Plus (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_TEST', 'Waste Plus (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_PROD', 'Waste Plus (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;


-- Add roles for WASTE_PLUS_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('WASTE_PLUS_VIEWER', 'Viewer', 'View waste data for a specific client', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_SUBMITTER', 'Submitter', 'Industry role to view, create and submit waste submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_DISTRICT', 'District', 'District role to view and approve submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_AREA', 'Area', 'Area waste specialist role to view, approve, and bill submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_ADMIN', 'Admin', 'Timber Pricing Branch role to create and edit all waste data', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for WASTE_PLUS_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('WASTE_PLUS_VIEWER', 'Viewer', 'View waste data for a specific client', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_SUBMITTER', 'Submitter', 'Industry role to view, create and submit waste submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_DISTRICT', 'District', 'District role to view and approve submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_AREA', 'Area', 'Area waste specialist role to view, approve, and bill submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_ADMIN', 'Admin', 'Timber Pricing Branch role to create and edit all waste data', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for WASTE_PLUS_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('WASTE_PLUS_VIEWER', 'Viewer', 'View waste data for a specific client', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_SUBMITTER', 'Submitter', 'Industry role to view, create and submit waste submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_DISTRICT', 'District', 'District role to view and approve submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_AREA', 'Area', 'Area waste specialist role to view, approve, and bill submissions', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('WASTE_PLUS_ADMIN', 'Admin', 'Timber Pricing Branch role to create and edit all waste data', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;
-- Create dev and test Cognito app clients for ICR
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_waste_plus_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_waste_plus_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_waste_plus_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'WASTE_PLUS_PROD'), CURRENT_USER, CURRENT_DATE)
;
