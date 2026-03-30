-- Update comment for fam_user_role_xref.expiry_date column

COMMENT ON COLUMN app_fam.fam_user_role_xref.expiry_date IS 'The date (in BC timezone) until which the user role assignment is valid. The assignment expires at midnight (00:00:00) following this date. NULL means no expiry.';
