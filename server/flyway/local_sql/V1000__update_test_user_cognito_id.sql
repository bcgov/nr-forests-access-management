-- This value needs to be in the DB in order for tests to work. If you want to
-- run the API locally, copy

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_b5ecdb094dfb4149a6a8445a0mangled@idir'
WHERE user_name = 'COGUSTAF';

-- add user_guid for COGUSTAF, as we use it as requester for tests, and requester should have user_guid
UPDATE app_fam.fam_user
SET user_guid = 'b5ecdb094dfb4149a6a8445a0mangled'
WHERE user_name = 'COGUSTAF';

UPDATE app_fam.fam_user
SET user_guid = 'b5ecdb094dfb4149a6a8445a0mangled'
WHERE user_name = 'COGUSTAF';

UPDATE app_fam.fam_user
SET cognito_user_id = 'test-idir_eb65e9d7828d4718aa6f4193cmangled@idir'
WHERE user_name = 'PTOLLEST';

-- add user_guid for PTOLLEST, as we use it as requester for tests, and requester should have user_guid
UPDATE app_fam.fam_user
SET user_guid = 'eb65e9d7828d4718aa6f4193cmangled'
WHERE user_name = 'PTOLLEST';