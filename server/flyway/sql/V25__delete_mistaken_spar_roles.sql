-- Delete any role assignments to the mistaken SPAR_TESTER roles
DELETE FROM app_fam.fam_user_role_xref WHERE role_id IN
    (SELECT role_id from app_fam.fam_role WHERE
        application_id IN (SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SPAR_DEV', 'SPAR_TEST', 'SPAR_PROD'))
        AND role_name IN ('SPR_NONMINISTRY_SUPERVISOR', 'SPAR_SPR_NONMIN_FOREST_GENETICS')
    )
;

-- Delete previously mistakenly created SPAR_TESTER roles for spar_dev, spar_test and spar_prod applications
DELETE FROM app_fam.fam_role WHERE
    application_id IN (
        SELECT application_id FROM app_fam.fam_application WHERE application_name IN ('SPAR_DEV', 'SPAR_TEST', 'SPAR_PROD')
    )
    AND role_name IN ('SPR_NONMINISTRY_SUPERVISOR', 'SPAR_SPR_NONMIN_FOREST_GENETICS')
;