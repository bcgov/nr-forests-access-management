-- Add new columns first_name, last_name and email into the fam_user table
-- We will display user information in the frontend dashboard table

ALTER TABLE
    app_fam.fam_user
ADD
    COLUMN first_name VARCHAR(50),
ADD
    COLUMN last_name VARCHAR(50),
ADD
    COLUMN email VARCHAR(250);

COMMENT ON COLUMN app_fam.fam_user.first_name IS 'The first name of the user';

COMMENT ON COLUMN app_fam.fam_user.last_name IS 'The last name of the user.';

COMMENT ON COLUMN app_fam.fam_user.email IS 'The email of the user.';

COMMENT ON COLUMN app_fam.fam_user.business_guid IS 'The business guid of the user if is a business bceid user.';