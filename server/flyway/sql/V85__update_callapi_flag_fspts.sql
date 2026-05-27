UPDATE app_fam.fam_role
SET call_api_flag = true
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('FSPTS_DEV', 'FSPTS_TEST', 'FSPTS_PROD'))
  AND role_name IN ('FSPTS_ADMINISTRATOR', 'FSPTS_DECISION_MAKER', 'FSPTS_REVIEWER', 'FSPTS_VIEW_ALL');
