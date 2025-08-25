-- Repeatable script should be idempotent.
-- When the script checksum is changed (script or placeholder value), the file will be run.
-- ${flyway:timestamp}

-- Description: Update fam_application_client.cognito_client_id to match current AWS account Cognito app clients.

-- Purpose:
--   * Ensure fam_application_client.cognito_client_id matches the correct Cognito clients in current AWS account.
--   * One main usage is for LZA migration when restoring data from ASEA then update to LZA Cognito app clients.

-- Enabled only when:
--   *  'v_update_cognito_clients_enabled' = true; (Although flyway run R script every time due to flyway:timestamp)

DO $$
DECLARE
    v_update_cognito_clients_enabled BOOLEAN := true;
BEGIN
    IF v_update_cognito_clients_enabled THEN
        WITH client_mapping AS (
            SELECT *
            FROM (VALUES
                ('FAM', '${client_id_fam_console}'),
                ('FOM_DEV', '${client_id_dev_fom_oidc_client}'),
                ('FOM_TEST', '${client_id_test_fom_oidc_client}'),
                ('FOM_PROD', '${client_id_prod_fom_oidc_client}'),
                ('SPAR_DEV', '${client_id_dev_spar_oidc_client}'),
                ('SPAR_TEST', '${client_id_test_spar_oidc_client}'),
                ('SPAR_PROD', '${client_id_prod_spar_oidc_client}'),
                ('CLIENT_DEV', '${client_id_dev_forest_client_oidc_client}'),
                ('CLIENT_TEST', '${client_id_test_forest_client_oidc_client}'),
                ('CLIENT_PROD', '${client_id_prod_forest_client_oidc_client}'),
                ('SILVA_DEV', '${client_id_dev_silva_oidc_client}'),
                ('SILVA_TEST', '${client_id_test_silva_oidc_client}'),
                ('SILVA_PROD', '${client_id_prod_silva_oidc_client}'),
                ('APT_DEV', '${client_id_dev_apt_oidc_client}'),
                ('APT_TEST', '${client_id_test_apt_oidc_client}'),
                ('APT_PROD', '${client_id_prod_apt_oidc_client}'),
                ('RESULTS_EXAM_DEV', '${client_id_dev_results_exam_oidc_client}'),
                ('RESULTS_EXAM_TEST', '${client_id_test_results_exam_oidc_client}'),
                ('RESULTS_EXAM_PROD', '${client_id_prod_results_exam_oidc_client}'),
                ('ILCR_DEV', '${client_id_dev_ilcr_oidc_client}'),
                ('ILCR_TEST', '${client_id_test_ilcr_oidc_client}'),
                ('ILCR_PROD', '${client_id_prod_ilcr_oidc_client}')
            ) AS t(application_name, cognito_client_id)
        )
        UPDATE app_fam.fam_application_client fac
        SET cognito_client_id = cm.cognito_client_id,
            update_user       = CURRENT_USER,
            update_date       = CURRENT_TIMESTAMP
        FROM client_mapping cm
        JOIN app_fam.fam_application fa
            ON fa.application_name = cm.application_name
        WHERE fac.application_id = fa.application_id;
    END IF;
END $$;
