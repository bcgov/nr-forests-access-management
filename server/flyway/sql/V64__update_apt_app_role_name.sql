-- Update app_fam.fam_role.role_name for application 'APT' with prfix 'APT_'
-- to be consistent with other applications.

-- APT 'VIEWER' role -> ROLE_NAME: "APT_VIEWER"
UPDATE app_fam.fam_role SET ROLE_NAME = 'APT_VIEWER' WHERE APPLICATION_ID in
    (select APPLICATION_ID from app_fam.fam_application where APPLICATION_NAME LIKE 'APT_%') AND ROLE_NAME = 'VIEWER';

-- APT 'EDITOR' role -> ROLE_NAME: "APT_EDITOR"
UPDATE app_fam.fam_role SET ROLE_NAME = 'APT_EDITOR' WHERE APPLICATION_ID in
    (select APPLICATION_ID from app_fam.fam_application where APPLICATION_NAME LIKE 'APT_%') AND ROLE_NAME = 'EDITOR';