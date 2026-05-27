-- Align LEXIS industry roles with forest-client scoped delegation.
-- Parent roles are abstract; concrete child roles are created by FAM during assignment.

UPDATE app_fam.fam_role
SET role_type_code = 'A',
    role_purpose = CASE
        WHEN role_name = 'LEXIS_INDUSTRY'
            THEN 'Industry role for LEXIS users requiring summary and offer workflows, scoped to a forest client.'
        WHEN role_name = 'LOG_EXPORT_INDUSTRY'
            THEN 'Industry role for LEXIS users requiring export-focused workflows, scoped to a forest client.'
        ELSE role_purpose
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
