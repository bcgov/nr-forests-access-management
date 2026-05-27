-- Add CSP applications and Cognito app clients

INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('CSP_DEV', 'CSP (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('CSP_TEST', 'CSP (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('CSP_PROD', 'CSP (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_csp_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'CSP_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_csp_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'CSP_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_csp_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'CSP_PROD'), CURRENT_USER, CURRENT_DATE)
;
