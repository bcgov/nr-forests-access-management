-- Increase length of role purpose column to 500

ALTER TABLE app_fam.fam_role
    ALTER COLUMN role_purpose SET DATA TYPE VARCHAR(500);