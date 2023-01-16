-- Rename application fom to fom_dev
UPDATE app_fam.fam_application
SET (application_name, application_description, update_user, update_date) =
	('fom_dev', 'Forest Operations Map DEV)', CURRENT_USER, CURRENT_DATE)
WHERE application_name = 'fom';

-- Rename role FOM_ACCESS_ADMIN to FOM_DEV_ACCESS_ADMIN
UPDATE app_fam.fam_role SET (role_name, role_purpose, update_user, update_date) =
	('FOM_DEV_ACCESS_ADMIN', 'Provides the privilege to assign or unassign all roles for FOM (DEV)', CURRENT_USER, CURRENT_DATE)
WHERE role_id =
	(SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FOM_ACCESS_ADMIN');

-- Create fom_test
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    create_user,
    create_date
)
VALUES (
    'fom_test',
    'Forest Operations Map (TEST)',
    CURRENT_USER,
    CURRENT_DATE
)
;

-- Create fom_test admin role
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES (
    'FOM_TEST_ACCESS_ADMIN',
    'Provides the privilege to assign or unassign all roles for FOM (TEST)',
    (select application_id from app_fam.fam_application where application_name = 'fom_test'),
    'C',
    CURRENT_USER,
    CURRENT_DATE
)
;

-- Create fom_prod
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    create_user,
    create_date
)
VALUES (
    'fom_prod',
    'Forest Operations Map (PROD)',
    CURRENT_USER,
    CURRENT_DATE
)
;

-- Create fom_prod admin role
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES (
    'FOM_PROD_ACCESS_ADMIN',
    'Provides the privilege to assign or unassign all roles for FOM (PROD)',
    (select application_id from app_fam.fam_application where application_name = 'fom_prod'),
    'C',
    CURRENT_USER,
    CURRENT_DATE
)
;

-- Create dev, test and prod clients for FOM

INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES (
    '${client_id_dev_fom_oidc_client}',
    (select application_id from app_fam.fam_application where application_name = 'fom_dev'),
    CURRENT_USER,
    CURRENT_DATE
)
;

INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES (
    '${client_id_test_fom_oidc_client}',
    (select application_id from app_fam.fam_application where application_name = 'fom_test'),
    CURRENT_USER,
    CURRENT_DATE
)
;

INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES (
    '${client_id_prod_fom_oidc_client}',
    (select application_id from app_fam.fam_application where application_name = 'fom_prod'),
    CURRENT_USER,
    CURRENT_DATE
)
;



