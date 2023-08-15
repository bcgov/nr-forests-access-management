-- This value needs to be in the DB in order for tests to work. If you want to
-- run the API locally, copy

UPDATE app_fam.fam_user
SET cognito_user_id = 'dev-idir_b5ecdb094dfb4149a6a8445a0mangled@idir'
WHERE user_name = 'COGUSTAF';

