-- This migration targets on making currently inconsistent 'create_date/update_date' to be consistent for their:
-- * data type: TIMESTAMP WITH TIME ZONE (at UTC)
-- * 'update_date' initial value: has the same intial value as 'create_date' and DEFAULT CURRENT_TIMESTAMP, with NOT NULL.


-- >> -- Table: fam_access_control_privilege -- << --
-- Change column type and convert existing values (with UTC timezone)
ALTER TABLE app_fam.fam_access_control_privilege
    ALTER COLUMN create_date TYPE timestamp with time zone USING create_date AT TIME ZONE 'UTC',
    ALTER COLUMN update_date TYPE timestamp with time zone USING update_date AT TIME ZONE 'UTC';

-- Update existing NULL values (update_date with create_date if null)
UPDATE app_fam.fam_access_control_privilege
    SET update_date = create_date WHERE update_date IS NULL;

-- Set default with NOT NULL constraint
ALTER TABLE app_fam.fam_access_control_privilege
    ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_app_environment -- << --
-- Update existing NULL values
UPDATE app_fam.fam_app_environment
    SET update_date = effective_date WHERE update_date IS NULL;

-- Set default with NOT NULL constraint
ALTER TABLE app_fam.fam_app_environment
    ALTER COLUMN effective_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_application -- << --
-- Update existing NULL values
UPDATE app_fam.fam_application
    SET update_date = create_date WHERE update_date IS NULL;

-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_application
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_application_admin -- << --
-- Change column type and convert existing values (with UTC timezone)
ALTER TABLE app_fam.fam_application_admin
    ALTER COLUMN create_date TYPE timestamp with time zone USING create_date AT TIME ZONE 'UTC',
    ALTER COLUMN update_date TYPE timestamp with time zone USING update_date AT TIME ZONE 'UTC';

-- Update existing NULL values
UPDATE app_fam.fam_application_admin
    SET update_date = create_date WHERE update_date IS NULL;

-- Set default with NOT NULL constraint
ALTER TABLE app_fam.fam_application_admin
    ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_application_client -- << --
-- Good and can skip.


-- >> -- Table: fam_application_group_xref -- << --
-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_application_group_xref
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_forest_client -- << --
-- Update existing NULL values
UPDATE app_fam.fam_forest_client
    SET update_date = create_date WHERE update_date IS NULL;

-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_forest_client
    ALTER COLUMN update_date SET NOT NULL;


--  >> -- Table: fam_group -- <<--
-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_group
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_group_role_xref -- << --
ALTER TABLE app_fam.fam_group_role_xref
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_privilege_change_audit -- << --
-- Good and can skip.


-- >> -- Table: fam_privilege_change_type -- << --
-- Change column type and convert existing values (with UTC timezone)
ALTER TABLE app_fam.fam_privilege_change_type
    ALTER COLUMN effective_date TYPE timestamp with time zone USING effective_date AT TIME ZONE 'UTC',
    ALTER COLUMN expiry_date TYPE timestamp with time zone USING expiry_date AT TIME ZONE 'UTC',
    ALTER COLUMN update_date TYPE timestamp with time zone USING update_date AT TIME ZONE 'UTC';

-- Update existing NULL values
UPDATE app_fam.fam_privilege_change_type
    SET update_date = effective_date WHERE update_date IS NULL;

-- Set default with NOT NULL constraint
ALTER TABLE app_fam.fam_privilege_change_type
    ALTER COLUMN effective_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_role -- << --
-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_role
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_role_type -- << --
-- Update existing NULL values
UPDATE app_fam.fam_role_type
    SET update_date = effective_date WHERE update_date IS NULL;

-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_role_type
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_user -- << --
-- Update existing NULL values
UPDATE app_fam.fam_user
    SET update_date = create_date WHERE update_date IS NULL;

-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_user
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_user_group_xref -- << --
-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_user_group_xref
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_user_role_xref -- << --
-- Update existing NULL values
UPDATE app_fam.fam_user_role_xref
    SET update_date = create_date WHERE update_date IS NULL;

-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_user_role_xref
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_user_terms_conditions -- << --
-- Change column type and convert existing values (with UTC timezone)
ALTER TABLE app_fam.fam_user_terms_conditions
    ALTER COLUMN create_date TYPE timestamp with time zone USING create_date AT TIME ZONE 'UTC',
    ALTER COLUMN update_date TYPE timestamp with time zone USING update_date AT TIME ZONE 'UTC';

-- Update existing NULL values
UPDATE app_fam.fam_user_terms_conditions
    SET update_date = create_date WHERE update_date IS NULL;

-- Set default with NOT NULL constraint
ALTER TABLE app_fam.fam_user_terms_conditions
    ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;


-- >> -- Table: fam_user_type_code -- << --
-- Update existing NULL values
UPDATE app_fam.fam_user_type_code
    SET update_date = effective_date WHERE update_date IS NULL;

-- Set NOT NULL constraint
ALTER TABLE app_fam.fam_user_type_code
    ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN update_date SET NOT NULL;