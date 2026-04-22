-- V81__adjust_rept_roles_call_api_flag.sql
-- Set call_api_flag to true for REPT_ADMIN and REPT_VIEWER roles in the REPT application

UPDATE app_fam.fam_role
SET call_api_flag = true
WHERE application_id in (select application_id from app_fam.fam_application where application_name IN ('REPT_DEV', 'REPT_TEST', 'REPT_PROD'))
  AND role_name IN ('REPT_ADMIN', 'REPT_VIEWER');
