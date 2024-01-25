-- Grant privileges for Admin Management API
-- -- on 'fam_role' for Read and Insert only.
GRANT SELECT, INSERT ON app_fam.fam_role TO ${admin_management_api_db_user}
;
-- -- on 'fam_forest_client' for Read only.
GRANT SELECT, INSERT ON app_fam.fam_forest_client TO ${admin_management_api_db_user}
;