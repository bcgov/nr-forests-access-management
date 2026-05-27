-- Replace placeholder LEXIS industry roles with submitter roles.
-- Keep ministry roles as concrete (C).
-- Provincial submitter is abstract (A) for forest-client scoped assignments.
-- Federal submitter is concrete (C) for a single named user.

UPDATE app_fam.fam_role
SET role_name = CASE
        WHEN role_name = 'LEXIS_INDUSTRY'
            THEN 'PROVINCIAL_SUBMITTER'
        WHEN role_name = 'LOG_EXPORT_INDUSTRY'
            THEN 'FEDERAL_SUBMITTER'
        ELSE role_name
    END,
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id IN (
    SELECT application_id
    FROM app_fam.fam_application
    WHERE application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD')
)
AND role_name IN ('LEXIS_INDUSTRY', 'LOG_EXPORT_INDUSTRY')
;

UPDATE app_fam.fam_role
SET display_name = CASE
        WHEN role_name = 'PROVINCIAL_SUBMITTER'
            THEN 'Provincial Submitter'
        WHEN role_name = 'FEDERAL_SUBMITTER'
            THEN 'Federal Submitter'
        ELSE display_name
    END,
    role_type_code = CASE
        WHEN role_name IN ('ADMIN', 'READ_ONLY', 'APPLICATION_APPROVER', 'EXEMPTION_APPROVER')
            THEN 'C'
        WHEN role_name = 'PROVINCIAL_SUBMITTER'
            THEN 'A'
        WHEN role_name = 'FEDERAL_SUBMITTER'
            THEN 'C'
        ELSE role_type_code
    END,
    role_purpose = CASE
        WHEN role_name = 'ADMIN'
            THEN 'Full administrative access to LEXIS.'
        WHEN role_name = 'READ_ONLY'
            THEN 'View-only access to LEXIS.'
        WHEN role_name = 'APPLICATION_APPROVER'
            THEN 'Approves LEXIS applications when approval is required.'
        WHEN role_name = 'EXEMPTION_APPROVER'
            THEN 'Approves and reviews LEXIS exemptions.'
        WHEN role_name = 'PROVINCIAL_SUBMITTER'
            THEN 'BCeID submitter role for provincial LEXIS application workflows, scoped to a forest client.'
        WHEN role_name = 'FEDERAL_SUBMITTER'
            THEN 'BCeID submitter role for federal LEXIS application workflows.'
        ELSE role_purpose
    END,
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id IN (
    SELECT application_id
    FROM app_fam.fam_application
    WHERE application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD')
)
AND role_name IN (
    'ADMIN',
    'READ_ONLY',
    'APPLICATION_APPROVER',
    'EXEMPTION_APPROVER',
    'PROVINCIAL_SUBMITTER',
    'FEDERAL_SUBMITTER'
)
;

-- Enable API access for all active LEXIS roles used by the current security model.
UPDATE app_fam.fam_role
SET call_api_flag = true
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name IN ('ADMIN', 'READ_ONLY', 'APPLICATION_APPROVER', 'EXEMPTION_APPROVER', 'PROVINCIAL_SUBMITTER', 'FEDERAL_SUBMITTER')
;
