-- Add a FOM_ADMIN role to FOM PROD
WITH application_ids AS (
    SELECT
        application_id,
        application_name
    FROM
        app_fam.fam_application
    WHERE
        application_name IN ('FOM_PROD')
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
    'Manages FOM data and performs administrative tasks.',
    application_id,
    'C',
    CURRENT_USER,
    CURRENT_DATE,
    'Admin'
FROM
    application_ids;
