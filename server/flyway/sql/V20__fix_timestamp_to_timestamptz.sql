-- Running upgrade V19 -> V20

-- Change date type to timestamptz for create_date and update_date
ALTER TABLE app_fam.fam_app_environment ALTER COLUMN effective_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_app_environment ALTER COLUMN expiry_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_app_environment ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_application ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_application ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_application_client ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_application_client ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_application_group_xref ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_application_group_xref ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_forest_client ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_forest_client ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_group ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_group ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_group_role_xref ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_group_role_xref ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_role ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_role ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_role_type ALTER COLUMN effective_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_role_type ALTER COLUMN expiry_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_role_type ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_user ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_user ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_user_group_xref ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_user_group_xref ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_user_role_xref ALTER COLUMN create_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_user_role_xref ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;

ALTER TABLE app_fam.fam_user_type_code ALTER COLUMN effective_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_user_type_code ALTER COLUMN expiry_date TYPE TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE app_fam.fam_user_type_code ALTER COLUMN update_date TYPE TIMESTAMP(6) WITH TIME ZONE;


-- Change default value for timestamptz column from localtimestamp to current_timestamp so it includes a time zone
ALTER TABLE app_fam.fam_application ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_application ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_application_client ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_application_client ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_application_group_xref ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_application_group_xref ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_forest_client ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_forest_client ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_group ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_group ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_group_role_xref ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_group_role_xref ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_role ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_role ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_role_type ALTER COLUMN effective_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_user ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_user ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_user_group_xref ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_user_group_xref ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_user_role_xref ALTER COLUMN create_date SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE app_fam.fam_user_role_xref ALTER COLUMN update_date SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE app_fam.fam_user_type_code ALTER COLUMN effective_date SET DEFAULT CURRENT_TIMESTAMP;