ALTER TABLE app_fam.fam_user alter COLUMN cognito_user_id type varchar(100);

ALTER TABLE app_fam.fam_application_client alter COLUMN update_date type timestamp(6) USING update_date::timestamp(6) without time zone;