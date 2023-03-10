-- Create spar_dev, spar_test and spar_prod applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('SPAR_DEV', 'Seed Planning and Registry Application (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('SPAR_TEST', 'Seed Planning and Registry Application (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('SPAR_PROD', 'Seed Planning and Registry Application (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;


-- Create spar_dev, spar_test and spar_prod admin roles
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SPAR_DEV_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for SPAR (DEV)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_TEST_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for SPAR (TEST)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_PROD_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for SPAR (PROD)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE)
;


-- Create a SPAR_TESTER roles for spar_dev, spar_test and spar_prod applications
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('USER_WRITE', 'A role used by SPAR for manual testing', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by SPAR for manual testing', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_WRITE', 'A role used by SPAR for manual testing', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by SPAR for manual testing', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_WRITE', 'A role used by SPAR for manual testing', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by SPAR for manual testing', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;


-- Create dev, test and prod clients for SPAR
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_spar_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_spar_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_spar_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), CURRENT_USER, CURRENT_DATE)
;
