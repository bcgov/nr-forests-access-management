-- Add CALL_API_FLAG BOOLEAN column to app_fam.fam_role table, defaulting to FALSE.
-- Purpose: to indicate whether the role has permission to call FAM external APIs.
ALTER TABLE app_fam.fam_role
ADD COLUMN CALL_API_FLAG BOOLEAN DEFAULT FALSE;

-- Add comment to CALL_API_FLAG column
COMMENT ON COLUMN app_fam.fam_role.CALL_API_FLAG IS 'Indicates whether the role has permission to call FAM external APIs.';

-- Set CALL_API_FLAG to TRUE for ILCR_ADMIN role
UPDATE app_fam.fam_role
SET CALL_API_FLAG = TRUE
WHERE role_name = 'ILCR_ADMIN';