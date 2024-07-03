-- Update unique constraint in fam user table to be user type code and user guid

-- For production data, we need to remove the existing duplication user records
-- These two users in production seem to have a username change, so we have same user_guid but different user_name for them
-- Dev and Test environment will ignore the deletion
DELETE FROM app_fam.fam_user WHERE user_id=943;
DELETE FROM app_fam.fam_user WHERE user_id=2257;


DROP INDEX app_fam.fam_usr_uk;

CREATE UNIQUE INDEX fam_usr_uk ON app_fam.fam_user(user_type_code, user_guid);