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
VALUES ('FREP_CHR_EDITOR_DISTRICT_DCC', 'Submitter (CHR-DCC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCS', 'Submitter (CHR-DCS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DOS', 'Submitter (CHR-DOS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DRM', 'Submitter (CHR-DRM)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DNI', 'Submitter (CHR-DNI)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPG', 'Submitter (CHR-DPG)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DVA', 'Submitter (CHR-DVA)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKM', 'Submitter (CHR-DKM)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMK', 'Submitter (CHR-DMK)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DFN', 'Submitter (CHR-DFN)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKA', 'Submitter (CHR-DKA)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMH', 'Submitter (CHR-DMH)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQU', 'Submitter (CHR-DQU)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCK', 'Submitter (CHR-DCK)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSQ', 'Submitter (CHR-DSQ)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSC', 'Submitter (CHR-DSC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCR', 'Submitter (CHR-DCR)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQC', 'Submitter (CHR-DQC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSI', 'Submitter (CHR-DSI)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DND', 'Submitter (CHR-DND)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSS', 'Submitter (CHR-DSS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPC', 'Submitter (CHR-DPC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSE', 'Submitter (CHR-DSE)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_DEV'), 'C', TRUE, CURRENT_USER, CURRENT_DATE)
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
VALUES ('FREP_CHR_EDITOR_DISTRICT_DCC', 'Submitter (CHR-DCC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCS', 'Submitter (CHR-DCS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DOS', 'Submitter (CHR-DOS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DRM', 'Submitter (CHR-DRM)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DNI', 'Submitter (CHR-DNI)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPG', 'Submitter (CHR-DPG)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DVA', 'Submitter (CHR-DVA)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKM', 'Submitter (CHR-DKM)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMK', 'Submitter (CHR-DMK)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DFN', 'Submitter (CHR-DFN)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKA', 'Submitter (CHR-DKA)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMH', 'Submitter (CHR-DMH)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQU', 'Submitter (CHR-DQU)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCK', 'Submitter (CHR-DCK)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSQ', 'Submitter (CHR-DSQ)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSC', 'Submitter (CHR-DSC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCR', 'Submitter (CHR-DCR)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQC', 'Submitter (CHR-DQC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSI', 'Submitter (CHR-DSI)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DND', 'Submitter (CHR-DND)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSS', 'Submitter (CHR-DSS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPC', 'Submitter (CHR-DPC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSE', 'Submitter (CHR-DSE)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_TEST'), 'C', TRUE, CURRENT_USER, CURRENT_DATE)
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
VALUES ('FREP_CHR_EDITOR_DISTRICT_DCC', 'Submitter (CHR-DCC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCS', 'Submitter (CHR-DCS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DOS', 'Submitter (CHR-DOS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DRM', 'Submitter (CHR-DRM)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DNI', 'Submitter (CHR-DNI)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPG', 'Submitter (CHR-DPG)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DVA', 'Submitter (CHR-DVA)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKM', 'Submitter (CHR-DKM)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMK', 'Submitter (CHR-DMK)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DFN', 'Submitter (CHR-DFN)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DKA', 'Submitter (CHR-DKA)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DMH', 'Submitter (CHR-DMH)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQU', 'Submitter (CHR-DQU)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCK', 'Submitter (CHR-DCK)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSQ', 'Submitter (CHR-DSQ)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSC', 'Submitter (CHR-DSC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DCR', 'Submitter (CHR-DCR)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DQC', 'Submitter (CHR-DQC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSI', 'Submitter (CHR-DSI)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DND', 'Submitter (CHR-DND)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSS', 'Submitter (CHR-DSS)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DPC', 'Submitter (CHR-DPC)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE),
       ('FREP_CHR_EDITOR_DISTRICT_DSE', 'Submitter (CHR-DSE)', 'Edit and submit CHR checklist.', (select application_id from app_fam.fam_application where application_name = 'FREP_PROD'), 'C', TRUE, CURRENT_USER, CURRENT_DATE)
;
