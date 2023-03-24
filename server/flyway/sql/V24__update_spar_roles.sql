-- Delete any role assignments to the SPAR_TESTER roles
DELETE FROM app_fam.fam_user_role_xref WHERE role_id IN
    (SELECT role_id from app_fam.fam_role WHERE application_id IN
        (SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SPAR_DEV', 'SPAR_TEST', 'SPAR_PROD'))
    )
;

-- Delete previously created SPAR_TESTER roles for spar_dev, spar_test and spar_prod applications
DELETE FROM app_fam.fam_role WHERE application_id IN (
    SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SPAR_DEV', 'SPAR_TEST', 'SPAR_PROD')
);

-- Create a roles for SPAR_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SPAR_SPR_BC_TIMBER_SALES', 'SPR_BC_TIMBER_SALES', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MIN_FOREST_GENETICS', 'SPR_MIN_FOREST_GENETICS', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MINISTRY_ORCHARD', 'SPR_MINISTRY_ORCHARD', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MINISTRY_VIEW_AND_REPT', 'SPR_MINISTRY_VIEW_AND_REPT', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMIN_FOREST_GENETICS', 'SPR_NONMIN_FOREST_GENETICS', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_ORCHARD', 'SPR_NONMINISTRY_ORCHARD', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_SUPERVISOR', 'SPR_NONMINISTRY_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPR_NONMINISTRY_SUPERVISOR', 'SPR_NONMINISTRY_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_VIEW_AND_REPT', 'SPR_NONMINISTRY_VIEW_AND_REPT', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_PRIVATE_NURSERY', 'SPR_PRIVATE_NURSERY', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_SILVICULTURE_STAFF', 'SPR_SILVICULTURE_STAFF', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_SILVICULTURE_SUPERVISOR', 'SPR_SILVICULTURE_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_IMPROVEMENT_HQ', 'SPR_TREE_IMPROVEMENT_HQ', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_ADMIN', 'SPR_TREE_SEED_CENTRE_ADMIN', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_FINANCE', 'SPR_TREE_SEED_CENTRE_FINANCE', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_STF_PRD', 'SPR_TREE_SEED_CENTRE_STF_PRD', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_STF_TST', 'SPR_TREE_SEED_CENTRE_STF_TST', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPR_ALT_SUPERVISOR', 'Additional alternative access for Supervisors', (select application_id from app_fam.fam_application where application_name = 'SPAR_DEV'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Create a roles for SPAR_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SPAR_SPR_BC_TIMBER_SALES', 'SPR_BC_TIMBER_SALES', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MIN_FOREST_GENETICS', 'SPR_MIN_FOREST_GENETICS', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MINISTRY_ORCHARD', 'SPR_MINISTRY_ORCHARD', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MINISTRY_VIEW_AND_REPT', 'SPR_MINISTRY_VIEW_AND_REPT', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMIN_FOREST_GENETICS', 'SPR_NONMIN_FOREST_GENETICS', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_ORCHARD', 'SPR_NONMINISTRY_ORCHARD', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_SUPERVISOR', 'SPR_NONMINISTRY_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPR_NONMINISTRY_SUPERVISOR', 'SPR_NONMINISTRY_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_VIEW_AND_REPT', 'SPR_NONMINISTRY_VIEW_AND_REPT', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_PRIVATE_NURSERY', 'SPR_PRIVATE_NURSERY', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_SILVICULTURE_STAFF', 'SPR_SILVICULTURE_STAFF', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_SILVICULTURE_SUPERVISOR', 'SPR_SILVICULTURE_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_IMPROVEMENT_HQ', 'SPR_TREE_IMPROVEMENT_HQ', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_ADMIN', 'SPR_TREE_SEED_CENTRE_ADMIN', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_FINANCE', 'SPR_TREE_SEED_CENTRE_FINANCE', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_STF_PRD', 'SPR_TREE_SEED_CENTRE_STF_PRD', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_STF_TST', 'SPR_TREE_SEED_CENTRE_STF_TST', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPR_ALT_SUPERVISOR', 'Additional alternative access for Supervisors', (select application_id from app_fam.fam_application where application_name = 'SPAR_TEST'), 'A', CURRENT_USER, CURRENT_DATE)
;

-- Create a roles for SPAR_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SPAR_SPR_BC_TIMBER_SALES', 'SPR_BC_TIMBER_SALES', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MIN_FOREST_GENETICS', 'SPR_MIN_FOREST_GENETICS', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MINISTRY_ORCHARD', 'SPR_MINISTRY_ORCHARD', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_MINISTRY_VIEW_AND_REPT', 'SPR_MINISTRY_VIEW_AND_REPT', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMIN_FOREST_GENETICS', 'SPR_NONMIN_FOREST_GENETICS', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_ORCHARD', 'SPR_NONMINISTRY_ORCHARD', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_SUPERVISOR', 'SPR_NONMINISTRY_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPR_NONMINISTRY_SUPERVISOR', 'SPR_NONMINISTRY_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_NONMINISTRY_VIEW_AND_REPT', 'SPR_NONMINISTRY_VIEW_AND_REPT', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_PRIVATE_NURSERY', 'SPR_PRIVATE_NURSERY', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_SILVICULTURE_STAFF', 'SPR_SILVICULTURE_STAFF', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_SILVICULTURE_SUPERVISOR', 'SPR_SILVICULTURE_SUPERVISOR', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_IMPROVEMENT_HQ', 'SPR_TREE_IMPROVEMENT_HQ', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_ADMIN', 'SPR_TREE_SEED_CENTRE_ADMIN', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_FINANCE', 'SPR_TREE_SEED_CENTRE_FINANCE', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_STF_PRD', 'SPR_TREE_SEED_CENTRE_STF_PRD', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPAR_SPR_TREE_SEED_CENTRE_STF_TST', 'SPR_TREE_SEED_CENTRE_STF_TST', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SPR_ALT_SUPERVISOR', 'Additional alternative access for Supervisors', (select application_id from app_fam.fam_application where application_name = 'SPAR_PROD'), 'A', CURRENT_USER, CURRENT_DATE)
;












