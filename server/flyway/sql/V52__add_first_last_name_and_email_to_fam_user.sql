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