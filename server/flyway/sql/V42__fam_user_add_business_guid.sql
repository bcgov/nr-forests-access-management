-- Add a new column business_guid into the fam_user table
-- For delegated admin who is possible business bceid user, we need their business_guid to decide the permission
ALTER TABLE
    app_fam.fam_user
ADD
    COLUMN business_guid VARCHAR(32);