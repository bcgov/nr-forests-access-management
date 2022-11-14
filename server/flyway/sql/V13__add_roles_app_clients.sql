INSERT INTO app_fam.fam_application_client (
    cognito_client_id,  
    application_id,  
    create_user     
)
VALUES (
    '${client_id_fam_console}',
    (select application_id from app_fam.fam_application where application_name = 'fam'),
    CURRENT_USER
)
;

INSERT INTO app_fam.fam_application_client (
    cognito_client_id,  
    application_id,  
    create_user     
)
VALUES (
    '${client_id_fom_public}',
    (select application_id from app_fam.fam_application where application_name = 'fom'),
    CURRENT_USER
)
;

INSERT INTO app_fam.fam_application_client (
    cognito_client_id,  
    application_id,  
    create_user     
)
VALUES (
    '${client_id_fom_ministry}',
    (select application_id from app_fam.fam_application where application_name = 'fom'),
    CURRENT_USER
)
;
