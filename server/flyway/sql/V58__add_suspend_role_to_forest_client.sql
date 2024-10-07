-- Add a CLIENT_SUSPEND role to Forest Client DEV and TEST
WITH application_ids AS (
    SELECT
        application_id,
        application_name
    FROM
        app_fam.fam_application
    WHERE
        application_name IN ('CLIENT_DEV', 'CLIENT_TEST')
)
INSERT INTO
    app_fam.fam_role (
        role_name,
        role_purpose,
        application_id,
        role_type_code,
        create_user,
        create_date,
        display_name
    )
SELECT
    'CLIENT_SUSPEND',
    'Ministry role to allow for the management of suspending clients',
    application_id,
    'C',
    CURRENT_USER,
    CURRENT_DATE,
    'Suspend'
FROM
    application_ids;
