-- This is a script to add local developers into FAM DB with their cognito user
-- IDs. When the correct values are in the DB, the JWT from the TEST-IDIR domain
-- in Cognito (from the FAM DEV environment, we use TEST-IDIR identity provider in local and dev environment) can be used to log into FAM and
-- the API logic that depends on finding the "requestor" still works.

-- For this script to run, the name of the file needs to match the flyway
-- convention (start with "V[#]__"). Recommend to rename this file locally and
-- make sure to git ignore the file so it doesn't get checked in. The cognito
-- user ids in this script have been intentionally mangled for security purposes.
-- If it is just for personal use, you only need to add your own IDIR guid
-- (available from the "users" tab in FAM DEV Cognito). We use upper cases for user_guid,
-- as the real user_guid are all in upper cases.

-- This script does not run in production (as it is in the "local_sql"
-- directory instead of the "sql" directory). FYI other scripts can be added to
-- "local_sql" to add test data that should not be used in production.

-- These users are already in the DB from an early production flyway script

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_b5ecdb094dfb4149a6a8445a0mangled@idir'
WHERE user_name = 'COGUSTAF';

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_0171bed26ffmanglede20651d1ee01@idir'
WHERE user_name = 'BVANDEGR';

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_e72a12c916amangled9e5dcdffae7@idir'
WHERE user_name = 'IANLIU';

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_eb65e9d7828d4718aa6f4193cmangled@idir'
WHERE user_name = 'PTOLLEST';

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-bceidbusiness_532905de0aa24923ae535428mangledf171bf13@bceidbusiness'
WHERE user_name = 'LOAD-3-TEST';

-- These users were never added through a script

INSERT INTO app_fam.fam_user (
    user_name,
    user_type_code,
    cognito_user_id,
    user_guid,
    create_user
)
VALUES
('CMENG','I','test-idir_a9888e8ac6a04mangled35df625bf@idir','A9888E8AC6A04MANGLED00135DF625BF',CURRENT_USER),
('OLIBERCH','I','test-idir_b7e191fa11dmangled9df1854b71@idir','B7E191FA11MANLED818EC79DF1854B71',CURRENT_USER),
('CYU','I','test-idir_234d9cbe4373457famangledd26ab162@idir','234D9CBE4373457ANLEDE215D26AB162',CURRENT_USER);