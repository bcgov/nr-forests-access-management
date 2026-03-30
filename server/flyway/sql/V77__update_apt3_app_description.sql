-- Update the application description for APT3
-- APT3 is not being used. Previously was created for APT modernization efforts, but the team reuse APT2 instead.

UPDATE app_fam.fam_application
SET application_description =
    REGEXP_REPLACE(application_description, 'Apportionment', 'Apportionment 3') || ' - Retired'
WHERE application_name LIKE 'APT3%';