-- migrate the fam roles to fam admin management table
-- first select all fam roles
-- and then select role_id and application_id this role is admin of, based on if the role name contains the application_name
-- -- for example, role name: FAM_ACCESS_ADMIN contains application name: FAM
-- --              role name: FOM_DEV_ACCESS_ADMIN contains application name: FOM_DEV
-- select the user_id and application_id the user is admin of, insert into fam_application_admin
INSERT INTO app_fam.fam_application_admin (user_id, application_id, create_user, create_date)
SELECT user_role_xref.user_id, application.application_id, CURRENT_USER, CURRENT_DATE
FROM app_fam.fam_role role
JOIN app_fam.fam_application application
    ON role.role_name LIKE '%' || application.application_name || '%'
JOIN app_fam.fam_user_role_xref user_role_xref
    ON role.role_id = user_role_xref.role_id
WHERE role.application_id=1;

