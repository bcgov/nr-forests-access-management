-- Add a role for CLIENT_DEV, CLIENT_TEST and CLIENT_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('CLIENT_ADMIN', 'Ministry role to create and edit all information', (select application_id from app_fam.fam_application where application_name = 'CLIENT_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_ADMIN', 'Ministry role to create and edit all information', (select application_id from app_fam.fam_application where application_name = 'CLIENT_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('CLIENT_ADMIN', 'Ministry role to create and edit all information', (select application_id from app_fam.fam_application where application_name = 'CLIENT_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;