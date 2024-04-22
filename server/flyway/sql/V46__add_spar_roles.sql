-- Delete any role assignments to the SPAR initial testing roles and old SPAR roles
DELETE FROM app_fam.fam_user_role_xref WHERE role_id IN
    (SELECT role_id from app_fam.fam_role WHERE application_id IN
        (SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SPAR_DEV', 'SPAR_TEST', 'SPAR_PROD'))
    )
;

-- Delete previously created the SPAR initial testing roles and old SPAR roles for spar_dev, spar_test and spar_prod applications
DELETE FROM app_fam.fam_role WHERE application_id IN (
    SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SPAR_DEV', 'SPAR_TEST', 'SPAR_PROD')
);

-- Add roles for SPAR_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SPAR_TSC_ADMIN', 'Allow ministry users to access SPAR administrative screens and perform administrative functions such as seedlot registration approval, or seedling request approval', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_MINISTRY_ORCHARD', 'Allow ministry users to access the A class registration screens and to create, review, update and submit forms. Ministry users may enter and update lots within their own Organizational Unit', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_NONMINISTRY_ORCHARD', 'Allow non ministry users to create, review, update and submit A class registration forms. Non-Ministry users may enter and update lots where their sign in client profile matches the Applicant Client', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SPAR_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SPAR_TSC_ADMIN', 'Allow ministry users to access SPAR administrative screens and perform administrative functions such as seedlot registration approval, or seedling request approval', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_MINISTRY_ORCHARD', 'Allow ministry users to access the A class registration screens and to create, review, update and submit forms. Ministry users may enter and update lots within their own Organizational Unit', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_NONMINISTRY_ORCHARD', 'Allow non ministry users to create, review, update and submit A class registration forms. Non-Ministry users may enter and update lots where their sign in client profile matches the Applicant Client', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SPAR_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SPAR_TSC_ADMIN', 'Allow ministry users to access SPAR administrative screens and perform administrative functions such as seedlot registration approval, or seedling request approval', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_MINISTRY_ORCHARD', 'Allow ministry users to access the A class registration screens and to create, review, update and submit forms. Ministry users may enter and update lots within their own Organizational Unit', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SPAR_NONMINISTRY_ORCHARD', 'Allow non ministry users to create, review, update and submit A class registration forms. Non-Ministry users may enter and update lots where their sign in client profile matches the Applicant Client', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE)
;