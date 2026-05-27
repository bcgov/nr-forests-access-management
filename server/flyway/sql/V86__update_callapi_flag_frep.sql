UPDATE app_fam.fam_role
SET call_api_flag = true
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('FREP_DEV', 'FREP_TEST', 'FREP_PROD'))
  AND role_name IN ('FREP_ADMIN', 'FREP_EDITOR', 'FREP_VIEW_ONLY');
