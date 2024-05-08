-- After migrating the admins to fam admin management table (V34) and with code base migration completed,
-- we can remove fam admin association for the users from fam_user_role_xref table and remove FAM roles
-- from fam_role table.

-- Just to be safe before deletion of records, migrate remaining admin user_role_xref again (if any),
-- if conflict on insert then do nothing.
WITH selected_admin_xrefs AS (
    SELECT user_role_xref.user_id, application.application_id, CURRENT_USER, CURRENT_DATE
    FROM app_fam.fam_role role
    JOIN app_fam.fam_application application
        ON role.role_name LIKE '%' || application.application_name || '%'
    JOIN app_fam.fam_user_role_xref user_role_xref
        ON role.role_id = user_role_xref.role_id
    WHERE role.application_id = (SELECT application_id FROM app_fam.fam_application
        WHERE application_name = 'FAM')
)
INSERT INTO app_fam.fam_application_admin (user_id, application_id, create_user, create_date)
SELECT user_id, application_id, CURRENT_USER, CURRENT_DATE
FROM selected_admin_xrefs
ON CONFLICT (user_id, application_id) DO NOTHING;

-- Remove admin user role association from fam_user_role_xref
DELETE FROM app_fam.fam_user_role_xref urx
WHERE urx.role_id in
    (select role_id
     from app_fam.fam_role
     where application_id = (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name = 'FAM')
);

-- Delete FAM roles
DELETE FROM app_fam.fam_role
    WHERE application_id in (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name = 'FAM');