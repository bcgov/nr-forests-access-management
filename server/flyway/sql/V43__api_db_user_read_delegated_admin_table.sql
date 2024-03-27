-- Grant SELECT privilege to API db user to get delegated admin access
GRANT SELECT ON app_fam.fam_access_control_privilege TO ${api_db_username}
;