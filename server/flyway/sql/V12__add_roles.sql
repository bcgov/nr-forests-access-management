INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user
)
VALUES (
    'FAM_ACCESS_ADMIN',
    'Provides the privilege to assign or unassign all roles for FAM',
    (select application_id from app_fam.fam_application where application_name = 'fam'),
    'C',
    CURRENT_USER
)
;

INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user
)
VALUES (
    'FOM_ACCESS_ADMIN',
    'Provides the privilege to assign or unassign all roles for FOM',
    (select application_id from app_fam.fam_application where application_name = 'fam'),
    'C',
    CURRENT_USER
)
;

INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user
)
VALUES (
    'FOM_SUBMITTER',
    'Provides the privilege to submit a FOM (on behalf of a specific forest client)',
    (select application_id from app_fam.fam_application where application_name = 'fom'),
    'A',
    CURRENT_USER
)
;

INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user
)
VALUES (
    'FOM_REVIEWER',
    'Provides the privilege to review all FOMs in the system',
    (select application_id from app_fam.fam_application where application_name = 'fom'),
    'C',
    CURRENT_USER
)
;