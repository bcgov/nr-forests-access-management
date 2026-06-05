-- Prefix previous CSP role names with "CSP_".
-- Add CSP_ENTRY role.

-- Update all CSP roles to add "CSP_" prefix
UPDATE app_fam.fam_role
SET role_name = 'CSP_ADMIN'
WHERE role_name = 'ADMIN'
  AND application_id IN (
    SELECT application_id FROM app_fam.fam_application
    WHERE application_name IN ('CSP_DEV', 'CSP_TEST', 'CSP_PROD')
  );

UPDATE app_fam.fam_role
SET role_name = 'CSP_APPROVER'
WHERE role_name = 'APPROVER'
  AND application_id IN (
    SELECT application_id FROM app_fam.fam_application
    WHERE application_name IN ('CSP_DEV', 'CSP_TEST', 'CSP_PROD')
  );

UPDATE app_fam.fam_role
SET role_name = 'CSP_VIEWER'
WHERE role_name = 'VIEWER'
  AND application_id IN (
    SELECT application_id FROM app_fam.fam_application
    WHERE application_name IN ('CSP_DEV', 'CSP_TEST', 'CSP_PROD')
  );

-- Add CSP_ENTRY role for CSP_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('CSP_ENTRY', 'Data Entry', 'Role for the manual entry of invoice data received from industry outside of ESF.', (SELECT application_id FROM app_fam.fam_application WHERE application_name = 'CSP_DEV'), 'C', CURRENT_USER, CURRENT_DATE);

-- Add CSP_ENTRY role for CSP_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('CSP_ENTRY', 'Data Entry', 'Role for the manual entry of invoice data received from industry outside of ESF.', (SELECT application_id FROM app_fam.fam_application WHERE application_name = 'CSP_TEST'), 'C', CURRENT_USER, CURRENT_DATE);

-- Add CSP_ENTRY role for CSP_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('CSP_ENTRY', 'Data Entry', 'Role for the manual entry of invoice data received from industry outside of ESF.', (SELECT application_id FROM app_fam.fam_application WHERE application_name = 'CSP_PROD'), 'C', CURRENT_USER, CURRENT_DATE);

