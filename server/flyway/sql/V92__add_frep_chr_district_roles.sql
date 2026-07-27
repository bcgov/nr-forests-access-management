-- Add CHR editor roles for FREP, one role per natural resource district.
-- Role name format: FREP_CHR_EDITOR_DISTRICT_<district code>
-- Applications FREP_DEV, FREP_TEST and FREP_PROD already exist (see V83).

-- Add CHR district roles for FREP_DEV
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    call_api_flag,
    create_user,
    create_date
)
VALUES ('FREP_CHR_EDITOR_DISTRICT_DCC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DOS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DRM', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DNI', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPG', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DVA', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKM', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMK', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DFN', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKA', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMH', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQU', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCK', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSQ', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCR', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSI', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DND', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSE', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE)
;

-- Add CHR district roles for FREP_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    call_api_flag,
    create_user,
    create_date
)
VALUES ('FREP_CHR_EDITOR_DISTRICT_DCC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DOS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DRM', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DNI', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPG', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DVA', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKM', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMK', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DFN', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKA', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMH', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQU', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCK', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSQ', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCR', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSI', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DND', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSE', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE)
;

-- Add CHR district roles for FREP_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    call_api_flag,
    create_user,
    create_date
)
VALUES ('FREP_CHR_EDITOR_DISTRICT_DCC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DOS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DRM', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DNI', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPG', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DVA', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKM', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMK', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DFN', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKA', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMH', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQU', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCK', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSQ', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCR', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSI', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DND', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSS', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPC', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSE', 'Decision Maker', 'Edit CHR in FREP.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE)
;
