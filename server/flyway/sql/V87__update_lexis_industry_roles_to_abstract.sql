-- Normalize LEXIS role names and role types.
-- Provincial submitter is abstract (A) because assignments are forest-client scoped.
-- Federal submitter is concrete (C) because there is a single named federal user.

UPDATE app_fam.fam_role
SET role_name = 'LEXIS_ADMIN',
    display_name = 'Administrator',
    role_type_code = 'C',
    role_purpose = 'Full administrative access to LEXIS.',
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name = 'ADMIN'
;

UPDATE app_fam.fam_role
SET role_name = 'LEXIS_READ_ONLY',
    display_name = 'Read Only',
    role_type_code = 'C',
    role_purpose = 'View-only access to LEXIS.',
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name = 'READ_ONLY'
;

UPDATE app_fam.fam_role
SET role_name = 'LEXIS_APPLICATION_APPROVER',
    display_name = 'Application Approver',
    role_type_code = 'C',
    role_purpose = 'Approves LEXIS applications when approval is required.',
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name = 'APPLICATION_APPROVER'
;

UPDATE app_fam.fam_role
SET role_name = 'LEXIS_EXEMPTION_APPROVER',
    display_name = 'Exemption Approver',
    role_type_code = 'C',
    role_purpose = 'Approves and reviews LEXIS exemptions.',
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name = 'EXEMPTION_APPROVER'
;

UPDATE app_fam.fam_role
SET role_name = 'LEXIS_PROVINCIAL_SUBMITTER',
    display_name = 'Provincial Submitter',
    role_type_code = 'A',
    role_purpose = 'BCeID submitter role for provincial LEXIS application workflows, scoped to a forest client.',
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name = 'LEXIS_INDUSTRY'
;

UPDATE app_fam.fam_role
SET role_name = 'LEXIS_FEDERAL_SUBMITTER',
    display_name = 'Federal Submitter',
    role_type_code = 'C',
    role_purpose = 'BCeID submitter role for federal LEXIS application workflows.',
    update_user = CURRENT_USER,
    update_date = CURRENT_TIMESTAMP
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name = 'LOG_EXPORT_INDUSTRY'
;

-- Enable API access for admin role only (least privilege). Expand in a future migration if needed.
UPDATE app_fam.fam_role
SET call_api_flag = true
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD'))
  AND role_name IN ('LEXIS_ADMIN')
;
