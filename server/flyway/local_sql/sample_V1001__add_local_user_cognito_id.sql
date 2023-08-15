-- This is a script to add local developers into FAM DB with their cognito user
-- IDs. When the correct values are in the DB, the JWT from the DEV-IDIR domain
-- in Cognito (from the FAM DEV environment) can be used to log into FAM and
-- the API logic that depends on finding the "requestor" still works.

-- For this script to run, the name of the file needs to match the flyway
-- convention (start with "V[#]__"). Recommend to rename this file locally and
-- make sure to git ignore the file so it doesn't get checked in. The cognito
-- user ids in this script have been intentionally mangled for security purposes.
-- If it is just for personal use, you only need to add your own IDIR guid
-- (available from the "users" tab in FAM DEV Cognito).

-- This script does not run in production (as it is in the "local_sql"
-- directory instead of the "sql" directory). FYI other scripts can be added to
-- "local_sql" to add test data that should not be used in production.

-- These users are already in the DB from an early production flyway script

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_b5ecdb094dmangledmangled@idir'
WHERE user_name = 'COGUSTAF';

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_0171bed26ffmanglede20651d1ee01@idir'
WHERE user_name = 'BVANDEGR';

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_e72a12c916amangled9e5dcdffae7@idir'
WHERE user_name = 'IANLIU';

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_eb65e9d782mangledc7d7f9b1@idir'
WHERE user_name = 'PTOLLEST';

-- These users were never added through a script

INSERT INTO app_fam.fam_user (
    user_name,
    user_type_code,
    cognito_user_id,
    create_user
)
VALUES

('JFERREIR','I','dev-idir_278f48bd9mangledf7e618d@idir',CURRENT_USER),
('NSAGLION','I','dev-idir_3f1414bd1mangled18a1293c40@idir',CURRENT_USER),
('CMENG','I','dev-idir_a9888e8ac6a04mangled35df625bf@idir',CURRENT_USER),
('OLIBERCH','I','dev-idir_b7e191fa11dmangled9df1854b71@idir',CURRENT_USER);

