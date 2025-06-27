-- Add a FOM_ADMIN role to FOM DEV and TEST
WITH application_ids AS (
    SELECT
        application_id,
        application_name
    FROM
        app_fam.fam_application
    WHERE
        application_name IN ('FOM_DEV', 'FOM_TEST')
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
    'FOM_ADMIN',
    'Manage and access FOM analytics summary data, with additional permissions to oversee and support administrative tasks.',
    application_id,
    'C',
    CURRENT_USER,
    CURRENT_DATE,
    'Admin'
FROM
    application_ids;
