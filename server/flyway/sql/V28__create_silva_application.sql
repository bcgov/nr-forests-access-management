-- Create silva_dev, silva_test and silva_prod applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('SILVA_DEV', ' (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('SILVA_TEST', 'Seed Planning and Registry Application (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('SILVA_PROD', 'Seed Planning and Registry Application (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;


-- Create silva_dev, silva_test and silva_prod admin roles
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SILVA_DEV_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for SILVA (DEV)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SILVA_TEST_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for SILVA (TEST)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SILVA_PROD_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for SILVA (PROD)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE)
;


-- Create a SILVA_TESTER roles for silva_dev, silva_test and silva_prod applications
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('USER_WRITE', 'A role used by SILVA for manual testing', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by SILVA for manual testing', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_WRITE', 'A role used by SILVA for manual testing', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by SILVA for manual testing', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_WRITE', 'A role used by SILVA for manual testing', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by SILVA for manual testing', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;


-- Create dev, test and prod clients for SILVA
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_silva_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_silva_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_silva_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), CURRENT_USER, CURRENT_DATE)
;
