-- Delete any role assignments to the CLIENT initial testing roles
DELETE FROM app_fam.fam_user_role_xref WHERE role_id IN
    (SELECT role_id from app_fam.fam_role WHERE application_id IN
        (SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('CLIENT_DEV', 'CLIENT_TEST', 'CLIENT_PROD'))
    )
;

-- Delete previously created CLIENT testing roles for client_dev, client_test and client_prod applications
DELETE FROM app_fam.fam_role WHERE application_id IN (
    SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('CLIENT_DEV', 'CLIENT_TEST', 'CLIENT_PROD')
);

-- Add a role for CLIENT_DEV, CLIENT_TEST and CLIENT_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('CLIENT_EDITOR', 'Ministry role to approve/reject submissions, create client records, and perform non-administrative edits to client records', (select application_id from app_fam.fam_application where application_name = 'CLIENT_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_EDITOR', 'Ministry role to approve/reject submissions, create client records, and perform non-administrative edits to client records', (select application_id from app_fam.fam_application where application_name = 'CLIENT_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_EDITOR', 'Ministry role to approve/reject submissions, create client records, and perform non-administrative edits to client records', (select application_id from app_fam.fam_application where application_name = 'CLIENT_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;