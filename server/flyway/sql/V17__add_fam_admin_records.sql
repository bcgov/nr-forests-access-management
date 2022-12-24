DELETE FROM app_fam.fam_user_role_xref;
DELETE FROM app_fam.fam_user;

INSERT INTO app_fam.fam_user (
    user_name,
    user_type_code,
    create_user
)
VALUES
('COGUSTAF','I',CURRENT_USER),
('BVANDEGR','I',CURRENT_USER),
('GATITEBI','I',CURRENT_USER),
('IANLIU','I',CURRENT_USER),
('PTOLLEST','I',CURRENT_USER);

INSERT INTO app_fam.fam_user_role_xref (
    user_id,
    role_id,
    create_user
)
VALUES
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'COGUSTAF'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FAM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'BVANDEGR'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FAM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'GATITEBI'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FAM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'IANLIU'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FAM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'PTOLLEST'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FAM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'COGUSTAF'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FOM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'BVANDEGR'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FOM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'GATITEBI'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FOM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'IANLIU'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FOM_ACCESS_ADMIN'),
    CURRENT_USER
),
(
    (SELECT user_id FROM app_fam.fam_user WHERE user_name = 'PTOLLEST'),
    (SELECT role_id FROM app_fam.fam_role WHERE role_name = 'FOM_ACCESS_ADMIN'),
    CURRENT_USER
);