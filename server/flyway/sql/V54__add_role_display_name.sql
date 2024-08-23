-- Add role display_name
ALTER TABLE app_fam.fam_role ADD COLUMN display_name VARCHAR(100);

COMMENT ON COLUMN app_fam.fam_role.display_name IS 'Human redable name for the role';

-- Migrate existing roles to set display_name below; for all 'C' and 'A' role types and all child roles.

-- CLIENT application roles: ('CLIENT_ADMIN%', 'CLIENT_EDITOR%', 'CLIENT_VIEWER%');
-- 'CLIENT_ADMIN' (role_type = 'C')
UPDATE app_fam.fam_role SET display_name = 'Admin'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'CLIENT_ADMIN%');

-- 'CLIENT_EDITOR' (role_type = 'C')
UPDATE app_fam.fam_role SET display_name = 'Editor'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'CLIENT_EDITOR%');

-- 'CLIENT_VIEWER' (role_type = 'C')
UPDATE app_fam.fam_role SET display_name = 'Viewer'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'CLIENT_VIEWER%');

--

-- FOM application roles: ('FOM_REVIEWER%', 'FOM_SUBMITTER%');
-- 'FOM_REVIEWER' (role_type = 'C')
UPDATE app_fam.fam_role SET display_name = 'Reviewer'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'FOM_REVIEWER%');

-- 'FOM_SUBMITTER' (role_type = 'A')
UPDATE app_fam.fam_role SET display_name = 'Submitter'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'FOM_SUBMITTER%');

--

-- SILVA application roles: ('Viewer%', 'Submitter%', 'Approver%', 'Planner%', 'Admin%')
-- 'Viewer' (role_type = 'C')
UPDATE app_fam.fam_role SET display_name = 'Viewer'
    WHERE role_id in (
    SELECT fr.role_id
	FROM app_fam.fam_role fr
	join app_fam.fam_application fa on fr.application_id = fa.application_id
	where fa.application_name like 'SILVA_%' and fr.role_name like 'Viewer%');

-- 'Submitter' (role_type = 'A')
UPDATE app_fam.fam_role SET display_name = 'Submitter'
    WHERE role_id in (
    SELECT fr.role_id
	FROM app_fam.fam_role fr
	join app_fam.fam_application fa on fr.application_id = fa.application_id
	where fa.application_name like 'SILVA_%' and fr.role_name like 'Submitter%');

-- 'Approver' (role_type = 'A')
UPDATE app_fam.fam_role SET display_name = 'Approver'
    WHERE role_id in (
    SELECT fr.role_id
	FROM app_fam.fam_role fr
	join app_fam.fam_application fa on fr.application_id = fa.application_id
	where fa.application_name like 'SILVA_%' and fr.role_name like 'Approver%');

-- 'Planner' (role_type = 'A')
UPDATE app_fam.fam_role SET display_name = 'Planner'
    WHERE role_id in (
    SELECT fr.role_id
	FROM app_fam.fam_role fr
	join app_fam.fam_application fa on fr.application_id = fa.application_id
	where fa.application_name like 'SILVA_%' and fr.role_name like 'Planner%');

-- 'Admin' (role_type = 'A')
UPDATE app_fam.fam_role SET display_name = 'Admin'
    WHERE role_id in (
    SELECT fr.role_id
	FROM app_fam.fam_role fr
	join app_fam.fam_application fa on fr.application_id = fa.application_id
	where fa.application_name like 'SILVA_%' and fr.role_name like 'Admin%');

--

-- SPAR application roles: ('SPAR_MINISTRY_ORCHARD%', 'SPAR_NONMINISTRY_ORCHARD%', 'SPAR_TSC_ADMIN%')
-- 'SPAR_MINISTRY_ORCHARD' (role_type = 'C')
UPDATE app_fam.fam_role SET display_name = 'Submitter (Ministry)'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'SPAR_MINISTRY_ORCHARD%');

-- 'SPAR_NONMINISTRY_ORCHARD' (role_type = 'A')
UPDATE app_fam.fam_role SET display_name = 'Submitter (Non-Ministry)'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'SPAR_NONMINISTRY_ORCHARD%');

-- 'SPAR_TSC_ADMIN' (role_type = 'C')
UPDATE app_fam.fam_role SET display_name = 'Admin'
    WHERE role_id in (
    SELECT role.role_id
    FROM app_fam.fam_role role
    WHERE role.role_name like 'SPAR_TSC_ADMIN%');