-- Running upgrade V20 -> V21
-- Update fam_application.application_name to upper case.

UPDATE app_fam.fam_application
SET (application_name, update_user, update_date) =
	('FAM', CURRENT_USER, CURRENT_DATE)
WHERE application_name = 'fam'
;

UPDATE app_fam.fam_application
SET (application_name, update_user, update_date) =
	('FOM_DEV', CURRENT_USER, CURRENT_DATE)
WHERE application_name = 'fom_dev'
;

UPDATE app_fam.fam_application
SET (application_name, update_user, update_date) =
	('FOM_TEST', CURRENT_USER, CURRENT_DATE)
WHERE application_name = 'fom_test'
;

UPDATE app_fam.fam_application
SET (application_name, update_user, update_date) =
	('FOM_PROD', CURRENT_USER, CURRENT_DATE)
WHERE application_name = 'fom_prod'
;
