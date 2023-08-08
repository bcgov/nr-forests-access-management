
-- Revoke default privileges previously assigned
ALTER DEFAULT privileges IN SCHEMA app_fam
REVOKE SELECT, INSERT, UPDATE, DELETE ON tables FROM ${api_db_username};;

-- Revoke broad permissions previously assigned
REVOKE SELECT, UPDATE, DELETE, INSERT ON ALL TABLES IN SCHEMA app_fam FROM ${api_db_username};

-- Grant specific permissions by function

-- List applications
GRANT SELECT ON app_fam.fam_application TO ${api_db_username};
GRANT SELECT ON app_fam.fam_app_environment TO ${api_db_username};

-- List user access
GRANT SELECT ON app_fam.fam_user_role_xref TO ${api_db_username};

GRANT SELECT ON app_fam.fam_user TO ${api_db_username};
GRANT SELECT ON app_fam.fam_user_type_code TO ${api_db_username};

GRANT SELECT ON app_fam.fam_role TO ${api_db_username};
GRANT SELECT ON app_fam.fam_role_type TO ${api_db_username};

GRANT SELECT ON app_fam.fam_forest_client TO ${api_db_username};

-- Grant/revoke user access
GRANT INSERT, DELETE ON app_fam.fam_user_role_xref TO ${api_db_username};
GRANT INSERT ON app_fam.fam_user TO ${api_db_username};
GRANT INSERT ON app_fam.fam_role TO ${api_db_username};
GRANT INSERT ON app_fam.fam_forest_client TO ${api_db_username};

-- To facilitate API unit testing (not needed directly by API lambda)
-- This is temporary tech debt to be removed in a future migration.
GRANT DELETE on app_fam.fam_user TO ${api_db_username};
GRANT DELETE on app_fam.fam_role TO ${api_db_username};
GRANT DELETE on app_fam.fam_forest_client TO ${api_db_username};


