-- Add CALL_API BOOLEAN column to app_fam.fam_role table, defaulting to FALSE.
-- The purpose of this column is to indicate whether the role has permission to call FAM external APIs.
ALTER TABLE app_fam.fam_role
ADD COLUMN CALL_API BOOLEAN DEFAULT FALSE;

-- Add comment to CALL_API column
COMMENT ON COLUMN app_fam.fam_role.CALL_API IS 'Indicates whether the role has permission to call FAM external APIs.';

-- Set CALL_API to TRUE for ILCR_ADMIN role
UPDATE app_fam.fam_role
SET CALL_API = TRUE
WHERE role_name = 'ILCR_ADMIN';