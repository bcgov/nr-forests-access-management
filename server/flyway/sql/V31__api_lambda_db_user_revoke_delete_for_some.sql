-- Continue from V30__ to further restrict permission after api tests \
-- have been adjusted with no need for data deletion after testing.
REVOKE DELETE on app_fam.fam_user FROM ${api_db_username};
REVOKE DELETE on app_fam.fam_role FROM ${api_db_username};
REVOKE DELETE on app_fam.fam_forest_client FROM ${api_db_username};