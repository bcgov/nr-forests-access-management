-- Update the application description of FOREST CLIENT
UPDATE
    app_fam.fam_application
SET
    application_description = 'Forests Client Management System (DEV)'
WHERE
    application_name = 'CLIENT_DEV';

UPDATE
    app_fam.fam_application
SET
    application_description = 'Forests Client Management System (TEST)'
WHERE
    application_name = 'CLIENT_TEST';

UPDATE
    app_fam.fam_application
SET
    application_description = 'Forests Client Management System (PROD)'
WHERE
    application_name = 'CLIENT_PROD';