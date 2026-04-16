-- Add FSPTS application and roles
-- FSPTS: (= FSP legacy app)
-- FSPTS: all roles are abstract roles (will be associated with forest clients)

-- Add FSPTS_DEV, FSPTS_TEST and FSPTS_PROD applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('FSPTS_DEV', 'Forest Stewardship Plan Tracking System (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_TEST', 'Forest Stewardship Plan Tracking System (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_PROD', 'Forest Stewardship Plan Tracking System (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for FSPTS_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('FSPTS_ADMINISTRATOR', 'Administrator', 'Add, change, delete, and view FSPs.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_DECISION_MAKER', 'Decision Maker', 'Approve FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_REVIEWER', 'Reviewer', 'Review FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_VIEW_ALL', 'View All', 'View all approved FSPs.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_SUBMITTER', 'Submitter', 'Submit FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_VIEW_ONLY', 'View Only', 'View approved FSPs submitted by organization.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for FSPTS_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('FSPTS_ADMINISTRATOR', 'Administrator', 'Add, change, delete, and view FSPs.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_DECISION_MAKER', 'Decision Maker', 'Approve FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_REVIEWER', 'Reviewer', 'Review FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_VIEW_ALL', 'View All', 'View all approved FSPs.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_SUBMITTER', 'Submitter', 'Submit FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_VIEW_ONLY', 'View Only', 'View approved FSPs submitted by organization.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for FSPTS_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('FSPTS_ADMINISTRATOR', 'Administrator', 'Add, change, delete, and view FSPs.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_DECISION_MAKER', 'Decision Maker', 'Approve FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_REVIEWER', 'Reviewer', 'Review FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_VIEW_ALL', 'View All', 'View all approved FSPs.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_SUBMITTER', 'Submitter', 'Submit FSPs, amendments, and extensions.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('FSPTS_VIEW_ONLY', 'View Only', 'View approved FSPs submitted by organization.', (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod Cognito app clients for FSPTS
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_fspts_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_fspts_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_fspts_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD'), CURRENT_USER, CURRENT_DATE)
;
