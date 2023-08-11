-- This is a script to add local developers into FAM DB with their cognito user
-- IDs. When the correct values are in the DB, the JWT from the DEV-IDIR domain
-- in Cognito (from the FAM DEV environment) can be used to log into FAM and
-- the API logic that depends on finding the "requestor" still works.

-- This script does not run in production (as it is in the "local_sql"
-- directory instead of the "sql" directory). FYI other scripts can be added to
-- "local_sql" to add test data that should not be used in production.

-- These users are already in the DB from an early production flyway script

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_b5ecdb094dfb4149a6a8445a01a96bf0@idir'
WHERE user_name = 'COGUSTAF';

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_0171bed26mangled20651d1ee01@idir'
WHERE user_name = 'BVANDEGR';

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_e72a12c91mangled1cf39e5dcdffae7@idir'
WHERE user_name = 'IANLIU';

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_eb65e9d78mangled6f4193c7d7f9b1@idir'
WHERE user_name = 'PTOLLEST';

-- These users were never added through a script

INSERT INTO app_fam.fam_user (
    user_name,
    user_type_code,
    cognito_user_id,
    create_user
)
VALUES

('JFERREIR','I','dev-idir_278f48bd95mangled0accf7e618d@idir',CURRENT_USER),
('NSAGLION','I','dev-idir_3f1414bd1amangledb3118a1293c40@idir',CURRENT_USER),
('CMENG','I','dev-idir_a9888e8ac6a04mangled0135df625bf@idir',CURRENT_USER),
('OLIBERCH','I','dev-idir_b7e191fa1mangledec79df1854b71@idir',CURRENT_USER);

