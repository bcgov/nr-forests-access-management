-- FREP role changes for DEV, TEST and PROD:
--   1. Remove FREP_VIEW_ONLY (added in V83).
--   2. FREP_EDITOR -> display name 'Submitter (SLR)', new role purpose.
--   3. FREP_ADMIN  -> new role purpose.
--
-- No FREP role is assigned to any user, so the delete has no dependent rows in
-- fam_user_role_xref or fam_access_control_privilege to clean up first.

-- Remove FREP_VIEW_ONLY
DELETE FROM app_fam.fam_role fr
USING app_fam.fam_application fa
WHERE fa.application_id = fr.application_id
  AND fa.application_name IN ('FREP_DEV', 'FREP_TEST', 'FREP_PROD')
  AND fr.role_name = 'FREP_VIEW_ONLY';

-- Update FREP_EDITOR display name and role purpose
UPDATE app_fam.fam_role fr
SET display_name = 'Submitter (SLR)',
    role_purpose = 'Edit and submit SLR checklist.',
    update_user = CURRENT_USER
FROM app_fam.fam_application fa
WHERE fa.application_id = fr.application_id
  AND fa.application_name IN ('FREP_DEV', 'FREP_TEST', 'FREP_PROD')
  AND fr.role_name = 'FREP_EDITOR';

-- Update FREP_ADMIN role purpose
UPDATE app_fam.fam_role fr
SET role_purpose = 'Add, edit, delete, and view FREP IMS.',
    update_user = CURRENT_USER
FROM app_fam.fam_application fa
WHERE fa.application_id = fr.application_id
  AND fa.application_name IN ('FREP_DEV', 'FREP_TEST', 'FREP_PROD')
  AND fr.role_name = 'FREP_ADMIN';
