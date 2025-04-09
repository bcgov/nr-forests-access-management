-- Update app_fam.fam_role.display_name for application 'APT'

-- APT 'VIEWER' role -> display_name: "View"
UPDATE app_fam.fam_role SET DISPLAY_NAME = 'Viewer' WHERE APPLICATION_ID in
    (select APPLICATION_ID from app_fam.fam_application where APPLICATION_NAME LIKE 'APT_%') AND ROLE_NAME = 'VIEWER';

-- APT 'EDITOR' role -> display_name: "Update"
UPDATE app_fam.fam_role SET DISPLAY_NAME = 'Editor' WHERE APPLICATION_ID in
    (select APPLICATION_ID from app_fam.fam_application where APPLICATION_NAME LIKE 'APT_%') AND ROLE_NAME = 'EDITOR';