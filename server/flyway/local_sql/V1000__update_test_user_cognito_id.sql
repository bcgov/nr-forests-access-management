-- This value needs to be in the DB in order for tests to work. If you want to
-- run the API locally, copy

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_b5ecdb094dfb4149a6a8445a0mangled@idir'
WHERE user_name = 'COGUSTAF';

-- add user_guid for COGUSTAF, as we use it as requester for tests, and requester should have user_guid
-- please note that this user is different from the test user we use in auth_funtion tests
UPDATE app_fam.fam_user
SET user_guid = 'B5ECDB094DFB4149A6A8445A0MANGLED'
WHERE user_name = 'COGUSTAF';

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_eb65e9d7828d4718aa6f4193cmangled@idir'
WHERE user_name = 'PTOLLEST';

-- add user_guid for PTOLLEST, as we use it as requester for tests, and requester should have user_guid
UPDATE app_fam.fam_user
SET user_guid = 'EB65E9D7828D4718AA6f4193CMANGLED'
WHERE user_name = 'PTOLLEST';