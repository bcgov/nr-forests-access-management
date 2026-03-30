-- Add fam_user_role_xref.expiry_date column: nullable
-- If expiry_date is NULL, the role assignment does not expire.

ALTER TABLE app_fam.fam_user_role_xref
    ADD COLUMN expiry_date TIMESTAMP(6) WITH TIME ZONE;

COMMENT ON COLUMN app_fam.fam_user_role_xref.expiry_date IS 'The date and time when the user role assignment is expired. NULL means no expiry.';
