-- Create ILCR_DEV, ILCR_TEST applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('ILCR_DEV', 'Interior Logging Cost Reporting Application (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('ILCR_TEST', 'Interior Logging Cost Reporting Application (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE)
;


-- Add roles for ILCR_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ILCR_ADMIN', 'Admin', 'Access to all mills, ability to set up access to ILCR for branch staff and licensees, ability to revise mill data, ability to set up new mills in ILCR, ability to update ILCR web pages, requires an IDIR.', (select application_id from app_fam.fam_application where application_name = 'ILCR_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ILCR_SUBMITTER', 'Submitter', 'Access to specific mill data as authorized by the ILCR Access Request Form, requires a BCeID', (select application_id from app_fam.fam_application where application_name = 'ILCR_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for ILCR_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('ILCR_ADMIN', 'Admin', 'Access to all mills, ability to set up access to ILCR for branch staff and licensees, ability to revise mill data, ability to set up new mills in ILCR, ability to update ILCR web pages, requires an IDIR.', (select application_id from app_fam.fam_application where application_name = 'ILCR_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('ILCR_SUBMITTER', 'Submitter', 'Access to specific mill data as authorized by the ILCR Access Request Form, requires a BCeID', (select application_id from app_fam.fam_application where application_name = 'ILCR_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Create dev and test Cognito app clients for ICR
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_ilcr_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'ILCR_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_ilcr_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'ILCR_TEST'), CURRENT_USER, CURRENT_DATE)
;
