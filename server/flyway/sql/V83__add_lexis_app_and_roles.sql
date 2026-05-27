-- Add LEXIS application and roles
-- Add LEXIS_DEV, LEXIS_TEST and LEXIS_PROD applications

INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('LEXIS_DEV', 'Log Exemption Information System (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('LEXIS_TEST', 'Log Exemption Information System (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('LEXIS_PROD', 'Log Exemption Information System (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for LEXIS_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ADMIN', 'Administrator', 'Full administrative access to LEXIS.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('READ_ONLY', 'Read Only', 'View-only access to LEXIS.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('APPLICATION_APPROVER', 'Application Approver', 'Approves LEXIS applications when approval is required.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('EXEMPTION_APPROVER', 'Exemption Approver', 'Approves and reviews LEXIS exemptions.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('LEXIS_INDUSTRY', 'Industry', 'Industry role for LEXIS users requiring summary and offer workflows.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('LOG_EXPORT_INDUSTRY', 'Log Export Industry', 'Industry role for LEXIS users requiring export-focused workflows.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for LEXIS_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ADMIN', 'Administrator', 'Full administrative access to LEXIS.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('READ_ONLY', 'Read Only', 'View-only access to LEXIS.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('APPLICATION_APPROVER', 'Application Approver', 'Approves LEXIS applications when approval is required.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('EXEMPTION_APPROVER', 'Exemption Approver', 'Approves and reviews LEXIS exemptions.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('LEXIS_INDUSTRY', 'Industry', 'Industry role for LEXIS users requiring summary and offer workflows.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('LOG_EXPORT_INDUSTRY', 'Log Export Industry', 'Industry role for LEXIS users requiring export-focused workflows.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for LEXIS_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ADMIN', 'Administrator', 'Full administrative access to LEXIS.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('READ_ONLY', 'Read Only', 'View-only access to LEXIS.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('APPLICATION_APPROVER', 'Application Approver', 'Approves LEXIS applications when approval is required.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('EXEMPTION_APPROVER', 'Exemption Approver', 'Approves and reviews LEXIS exemptions.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('LEXIS_INDUSTRY', 'Industry', 'Industry role for LEXIS users requiring summary and offer workflows.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('LOG_EXPORT_INDUSTRY', 'Log Export Industry', 'Industry role for LEXIS users requiring export-focused workflows.', (select application_id from app_fam.fam_application where application_name = 'LEXIS_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod Cognito app clients for LEXIS
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_lexis_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'LEXIS_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_lexis_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'LEXIS_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_lexis_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'LEXIS_PROD'), CURRENT_USER, CURRENT_DATE)
;
