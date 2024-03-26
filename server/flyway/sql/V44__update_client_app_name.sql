-- Update the application description of FOREST CLIENT
UPDATE
    app_fam.fam_application
SET
    application_description = 'Forests Client Management System'
WHERE
    application_name = 'CLIENT_DEV'
    or application_name = 'CLIENT_TEST'
    or application_name = 'CLIENT_PROD';