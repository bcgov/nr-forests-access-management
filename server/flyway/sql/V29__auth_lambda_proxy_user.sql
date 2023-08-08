
CREATE USER ${auth_lambda_db_user} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD '${auth_lambda_db_password}';

-- Needed to access anything in the schema
GRANT USAGE ON SCHEMA app_fam TO ${auth_lambda_db_user};

-- Update and insert on app_fam needed for creating/updating the user record
GRANT UPDATE, INSERT ON app_fam.fam_user TO ${auth_lambda_db_user};

-- Select on these tables needed to determine for the given application (cognito client) which roles the user can access
GRANT SELECT ON app_fam.fam_user TO ${auth_lambda_db_user};
GRANT SELECT ON app_fam.fam_role TO ${auth_lambda_db_user};
GRANT SELECT ON app_fam.fam_application TO ${auth_lambda_db_user};
GRANT SELECT ON app_fam.fam_application_client TO ${auth_lambda_db_user};
GRANT SELECT ON app_fam.fam_user_role_xref TO ${auth_lambda_db_user};

