-- Update roles in each environment

--DEV
UPDATE app_fam.fam_role
SET role_type_code = 'C'
WHERE role_name in ('FSPTS_ADMINISTRATOR', 'FSPTS_DECISION_MAKER', 'FSPTS_REVIEWER', 'FSPTS_VIEW_ALL')
  AND application_id = (select application_id from app_fam.fam_application where application_name = 'FSPTS_DEV');

--TEST
UPDATE app_fam.fam_role
SET role_type_code = 'C'
WHERE role_name in ('FSPTS_ADMINISTRATOR', 'FSPTS_DECISION_MAKER', 'FSPTS_REVIEWER', 'FSPTS_VIEW_ALL')
  AND application_id = (select application_id from app_fam.fam_application where application_name = 'FSPTS_TEST');

--PROD
UPDATE app_fam.fam_role
SET role_type_code = 'C'
WHERE role_name in ('FSPTS_ADMINISTRATOR', 'FSPTS_DECISION_MAKER', 'FSPTS_REVIEWER', 'FSPTS_VIEW_ALL')
  AND application_id = (select application_id from app_fam.fam_application where application_name = 'FSPTS_PROD');

