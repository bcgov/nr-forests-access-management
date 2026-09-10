-- NEXCOL users sign in with Business BCeID to view federal applications in LEXIS.
-- This is a concrete role: federal access has no forest-client assignment.
-- LEXIS enforces the identity provider and read-only federal permissions.
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
SELECT 'LEXIS_FEDERAL_READ_ONLY',
       'Federal Read Only',
       'Business BCeID view-only access to all federal application searches and details in LEXIS. No provincial, report, administration, or write access.',
       application_id,
       'C',
       CURRENT_USER,
       CURRENT_TIMESTAMP
FROM app_fam.fam_application
WHERE application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD');
