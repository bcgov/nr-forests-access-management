-- Change description: Update two SPAR roles for fam_role.display_name to:
-- * Submitter (Ministry) to Submitter Ministry (Orchard),
-- * Submitter (Non-Ministry) to Submitter Non-Ministry (Orchard)
-- * DEV/TEST/PROD SPAR application roles.

UPDATE app_fam.fam_role
SET display_name = CASE
    WHEN display_name = 'Submitter (Ministry)' THEN 'Submitter Ministry (Orchard)'
    WHEN display_name = 'Submitter (Non-Ministry)' THEN 'Submitter Non-Ministry (Orchard)'
END
WHERE display_name IN ('Submitter (Ministry)', 'Submitter (Non-Ministry)');


-- Change description: Insert two new SPAR roles:
-- 1. display name: Submitter (Tree Seed Centre), role_purpose: Allow ministry user to access cone and seed processing, testing and inventory management screens in the CONSEP module of SPAR.
-- 2. display name: Supervisor (Tree Seed Centre), role_purpose: Allow ministry user to access CONSEP administrative screens and perform administrative function such as deletions and unaccepting results.
-- * DEV/TEST/PROD SPAR applications.
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date,
    update_date
)
VALUES
    ('SPAR_TSC_SUBMITTER', 'Submitter (Tree Seed Centre)', 'Allow ministry user to access cone and seed processing, testing and inventory management screens in the CONSEP module of SPAR.', (SELECT application_id FROM app_fam.fam_application WHERE application_name = 'SPAR_DEV'), 'C', CURRENT_USER, CURRENT_DATE, CURRENT_DATE),
    ('SPAR_TSC_SUBMITTER', 'Submitter (Tree Seed Centre)', 'Allow ministry user to access cone and seed processing, testing and inventory management screens in the CONSEP module of SPAR.', (SELECT application_id FROM app_fam.fam_application WHERE application_name = 'SPAR_TEST'), 'C', CURRENT_USER, CURRENT_DATE, CURRENT_DATE),
    ('SPAR_TSC_SUBMITTER', 'Submitter (Tree Seed Centre)', 'Allow ministry user to access cone and seed processing, testing and inventory management screens in the CONSEP module of SPAR.', (SELECT application_id FROM app_fam.fam_application WHERE application_name = 'SPAR_PROD'), 'C', CURRENT_USER, CURRENT_DATE, CURRENT_DATE),

    ('SPAR_TSC_SUPERVISOR', 'Supervisor (Tree Seed Centre)', 'Allow ministry user to access CONSEP administrative screens and perform administrative function such as deletions and unaccepting results.', (SELECT application_id FROM app_fam.fam_application WHERE application_name like 'SPAR_DEV'), 'C', CURRENT_USER, CURRENT_DATE, CURRENT_DATE),
    ('SPAR_TSC_SUPERVISOR', 'Supervisor (Tree Seed Centre)', 'Allow ministry user to access CONSEP administrative screens and perform administrative function such as deletions and unaccepting results.', (SELECT application_id FROM app_fam.fam_application WHERE application_name like 'SPAR_TEST'), 'C', CURRENT_USER, CURRENT_DATE, CURRENT_DATE),
    ('SPAR_TSC_SUPERVISOR', 'Supervisor (Tree Seed Centre)', 'Allow ministry user to access CONSEP administrative screens and perform administrative function such as deletions and unaccepting results.', (SELECT application_id FROM app_fam.fam_application WHERE application_name like 'SPAR_PROD'), 'C', CURRENT_USER, CURRENT_DATE, CURRENT_DATE);