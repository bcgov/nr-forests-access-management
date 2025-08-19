-- Add roles for ILCR_DEV for testing only
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('LZA_TESTING', 'LZA Testing', 'Testing role for LZA', (select application_id from app_fam.fam_application where application_name = 'ILCR_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;