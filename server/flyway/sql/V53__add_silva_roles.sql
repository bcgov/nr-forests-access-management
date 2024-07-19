-- Delete any role assignments to the SILVA initial testing roles
DELETE FROM app_fam.fam_user_role_xref WHERE role_id IN
    (SELECT role_id from app_fam.fam_role WHERE application_id IN
        (SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SILVA_DEV', 'SILVA_TEST', 'SILVA_PROD'))
    )
;

-- Delete previously created the SILVA initial testing roles for SILVA_DEV, SILVA_TEST and SILVA_PROD applications
DELETE FROM app_fam.fam_role WHERE application_id IN (
    SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SILVA_DEV', 'SILVA_TEST', 'SILVA_PROD')
);

-- Add roles for SILVA_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('Viewer', 'View Silva data for assigned clients or organizational units.', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('Submitter', 'View and update Silva data, including activity reporting and milestone declarations.', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Approver', 'Review and approve or reject submissions on behalf of the Minister or designate.', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Planner', 'Conduct planning and managing activities for government-funded programs.', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Admin', 'Manages Silva data and performs administrative tasks.', (select application_id from app_fam.fam_application where application_name = 'SILVA_DEV'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SILVA_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('Viewer', 'View Silva data for assigned clients or organizational units.', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('Submitter', 'View and update Silva data, including activity reporting and milestone declarations.', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Approver', 'Review and approve or reject submissions on behalf of the Minister or designate.', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Planner', 'Conduct planning and managing activities for government-funded programs.', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Admin', 'Manages Silva data and performs administrative tasks.', (select application_id from app_fam.fam_application where application_name = 'SILVA_TEST'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SILVA_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('Viewer', 'View Silva data for assigned clients or organizational units.', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('Submitter', 'View and update Silva data, including activity reporting and milestone declarations.', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Approver', 'Review and approve or reject submissions on behalf of the Minister or designate.', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Planner', 'Conduct planning and managing activities for government-funded programs.', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('Admin', 'Manages Silva data and performs administrative tasks.', (select application_id from app_fam.fam_application where application_name = 'SILVA_PROD'), 'A', CURRENT_USER, CURRENT_DATE)
;