-- Description: Update descriptions for privilege change types (GRANT, REVOKE, UPDATE) in app_fam.fam_privilege_change_type.

-- Update descriptions for existing records
UPDATE app_fam.fam_privilege_change_type
SET description = 'Role added'
WHERE privilege_change_type_code = 'GRANT';

UPDATE app_fam.fam_privilege_change_type
SET description = 'Role revoked'
WHERE privilege_change_type_code = 'REVOKE';

UPDATE app_fam.fam_privilege_change_type
SET description = 'Role updated'
WHERE privilege_change_type_code = 'UPDATE';

-- Ensure update_date is updated
UPDATE app_fam.fam_privilege_change_type
SET update_date = now()
WHERE privilege_change_type_code IN ('GRANT', 'REVOKE', 'UPDATE');
