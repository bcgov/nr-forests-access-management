-- migrate the fam roles to fam admin management table
-- first select all fam roles
-- and then select role_id and application_id this role is admin of, based on if the role name contains the application_name
-- -- for example, role name: FAM_ACCESS_ADMIN contains application name: FAM
-- --              role name: FOM_DEV_ACCESS_ADMIN contains application name: FOM_DEV
-- select the user_id and application_id the user is admin of, insert into fam_application_admin
INSERT INTO fam_application_admin (user_id, application_id, create_user, create_date)
SELECT  admins.user_id, admins.application_id, CURRENT_USER, CURRENT_DATE FROM (
    SELECT user_id, application_id FROM fam_user_role_xref c JOIN (
        SELECT role_id, application_id FROM fam_application a JOIN (
            SELECT role_id, role_name FROM fam_role WHERE application_id=1
        ) b ON b.role_name LIKE '%' || a.application_name || '%'
    ) d ON c.role_id = d.role_id
) admins;



