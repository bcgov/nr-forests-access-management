-- Add CALL_API BOOLEAN column to app_fam.fam_role table, defaulting to FALSE.
-- The purpose of this column is to indicate whether the role has permission to call FAM external APIs.
ALTER TABLE app_fam.fam_role
ADD COLUMN CALL_API BOOLEAN DEFAULT FALSE;

-- Set CALL_API to TRUE for ILCR_ADMIN role
UPDATE app_fam.fam_role
SET CALL_API = TRUE
WHERE role = 'ILCR_ADMIN';