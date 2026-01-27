-- Add ISP application and roles
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('ISP_DEV', 'Interior Selling Price (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('ISP_TEST', 'Interior Selling Price (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('ISP_PROD', 'Interior Selling Price (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for ISP_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ISP_ADMIN', 'Admin', 'Users have administrative access.', (select application_id from app_fam.fam_application where application_name = 'ISP_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ISP_APPROVER', 'Approver', 'Users can approve content.', (select application_id from app_fam.fam_application where application_name = 'ISP_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ISP_SUBMITTER', 'Submitter', 'Users can submit content.', (select application_id from app_fam.fam_application where application_name = 'ISP_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for ISP_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ISP_ADMIN', 'Admin', 'Users have administrative access.', (select application_id from app_fam.fam_application where application_name = 'ISP_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ISP_APPROVER', 'Approver', 'Users can approve content.', (select application_id from app_fam.fam_application where application_name = 'ISP_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ISP_SUBMITTER', 'Submitter', 'Users can submit content.', (select application_id from app_fam.fam_application where application_name = 'ISP_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for ISP_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ISP_ADMIN', 'Admin', 'Users have administrative access.', (select application_id from app_fam.fam_application where application_name = 'ISP_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ISP_APPROVER', 'Approver', 'Users can approve content.', (select application_id from app_fam.fam_application where application_name = 'ISP_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ISP_SUBMITTER', 'Submitter', 'Users can submit content.', (select application_id from app_fam.fam_application where application_name = 'ISP_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod Cognito app clients for ISP
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_isp_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'ISP_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_isp_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'ISP_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_isp_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'ISP_PROD'), CURRENT_USER, CURRENT_DATE)
