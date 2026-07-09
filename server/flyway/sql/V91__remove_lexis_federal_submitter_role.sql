-- Remove deprecated LEXIS federal submitter role.
-- Federal submissions are authorized by a machine-to-machine Keycloak scope.

DELETE FROM app_fam.fam_role fr
USING app_fam.fam_application fa
WHERE fa.application_id = fr.application_id
  AND fa.application_name IN ('LEXIS_DEV', 'LEXIS_TEST', 'LEXIS_PROD')
  AND fr.role_name = 'LEXIS_FEDERAL_SUBMITTER';
