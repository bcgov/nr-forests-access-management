-- Create user type codes to handle 3 types of bcsc users

INSERT INTO app_fam.fam_user_type_code (user_type_code, description) VALUES ('CD', 'User Type for DEV BCSC users.');
INSERT INTO app_fam.fam_user_type_code (user_type_code, description) VALUES ('CT', 'User Type for TEST BCSC users.');
INSERT INTO app_fam.fam_user_type_code (user_type_code, description) VALUES ('CP', 'User Type for PROD BCSC users.');

-- Blank out the cognito_user_id field since we are going to have all new users anyway

UPDATE app_fam.fam_user SET cognito_user_id = NULL;

-- Create forest_client_dev, forest_client_test and forest_client_prod applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('CLIENT_DEV', 'Forest Client (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_TEST', 'Forest Client (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_PROD', 'Forest Client (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod clients for forest_client
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_forest_client_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'CLIENT_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_forest_client_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'CLIENT_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_forest_client_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'CLIENT_PROD'), CURRENT_USER, CURRENT_DATE)
;

-- Create forest_client_dev, forest_client_test and forest_client_prod admin roles
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('CLIENT_DEV_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for CLIENT (DEV)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_TEST_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for CLIENT (TEST)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_PROD_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for CLIENT (PROD)', (select application_id from app_fam.fam_application where application_name = 'FAM'), 'C', CURRENT_USER, CURRENT_DATE)
;


-- Create a CLIENT_TESTER roles for forest_client_dev, forest_client_test and forest_client_prod applications
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('USER_WRITE', 'A role used by CLIENT for manual testing', (select application_id from app_fam.fam_application where application_name = 'CLIENT_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by CLIENT for manual testing', (select application_id from app_fam.fam_application where application_name = 'CLIENT_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_WRITE', 'A role used by CLIENT for manual testing', (select application_id from app_fam.fam_application where application_name = 'CLIENT_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by CLIENT for manual testing', (select application_id from app_fam.fam_application where application_name = 'CLIENT_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_WRITE', 'A role used by CLIENT for manual testing', (select application_id from app_fam.fam_application where application_name = 'CLIENT_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('USER_READ', 'A role used by CLIENT for manual testing', (select application_id from app_fam.fam_application where application_name = 'CLIENT_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Update existing fam client application

UPDATE app_fam.fam_application_client
    SET
        cognito_client_id = '${client_id_fam_console}',
        update_user = CURRENT_USER,
        update_date = CURRENT_DATE
    WHERE
        application_id = (select application_id from app_fam.fam_application where application_name = 'FAM');

-- Remove fom_dev application_client records. There were 3 of them, 2 unused.
-- Better to clean them up at this point

DELETE FROM app_fam.fam_application_client WHERE
    application_id = (select application_id from app_fam.fam_application where application_name = 'FOM_DEV');

-- Update existing fom client applications

-- Create dev client for FOM
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES (
    '${client_id_dev_fom_oidc_client}',
    (select application_id from app_fam.fam_application where application_name = 'FOM_DEV'),
    CURRENT_USER,
    CURRENT_DATE
);

UPDATE app_fam.fam_application_client
    SET
        cognito_client_id = '${client_id_test_fom_oidc_client}',
        update_user = CURRENT_USER,
        update_date = CURRENT_DATE
    WHERE
        application_id = (select application_id from app_fam.fam_application where application_name = 'FOM_TEST');

UPDATE app_fam.fam_application_client
    SET
        cognito_client_id = '${client_id_prod_fom_oidc_client}',
        update_user = CURRENT_USER,
        update_date = CURRENT_DATE
    WHERE
        application_id = (select application_id from app_fam.fam_application where application_name = 'FOM_PROD');

-- Update existing SPAR client applications

UPDATE app_fam.fam_application_client
    SET
        cognito_client_id = '${client_id_dev_spar_oidc_client}',
        update_user = CURRENT_USER,
        update_date = CURRENT_DATE
    WHERE
        application_id = (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV');

UPDATE app_fam.fam_application_client
    SET
        cognito_client_id = '${client_id_test_spar_oidc_client}',
        update_user = CURRENT_USER,
        update_date = CURRENT_DATE
    WHERE
        application_id = (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST');

UPDATE app_fam.fam_application_client
    SET
        cognito_client_id = '${client_id_prod_spar_oidc_client}',
        update_user = CURRENT_USER,
        update_date = CURRENT_DATE
    WHERE
        application_id = (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD');


