-- Add SCS application and roles

-- Add SCS_DEV, SCS_TEST and SCS_PROD applications
INSERT INTO app_fam.fam_application (
    application_name,
    application_description,
    app_environment,
    create_user,
    create_date
)
VALUES ('SCS_DEV', 'SCS - Scale Control System (DEV)', 'DEV', CURRENT_USER, CURRENT_DATE),
       ('SCS_TEST', 'SCS - Scale Control System (TEST)', 'TEST', CURRENT_USER, CURRENT_DATE),
       ('SCS_PROD', 'SCS - Scale Control System (PROD)', 'PROD', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SCS_DEV
-- Concrete ('C') roles are IDIR-based, assigned directly to a user.
-- Abstract ('A') roles are BCeID-based, scoped to a forest_client (delegated access).
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SCS_BRANCH_SYS_SUPPORT', 'Branch System Support', 'Branch system support for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CE_TECHNICIAN', 'Technician', 'Technician role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CHECK_SCALER', 'Check Scaler', 'Check scaler role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CLERICAL', 'Clerical', 'Clerical role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_DIST_MANAGER', 'District Manager', 'District manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_DIST_SCALING_MANAGER', 'District Scaling Manager', 'District scaling manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_INDUSTRY_SCALER', 'Industry Scaler', 'Industry scaler role for the SCS application, scoped to a forest client.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SCS_OWNER', 'Scale Site Owner', 'Scale site owner role for the SCS application, scoped to a forest client.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SCS_REGIONAL_MANAGER', 'Regional Manager', 'Regional manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_REGIONAL_SCALING_MANAGER', 'Regional Scaling Manager', 'Regional scaling manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_SYS_ADMIN', 'Admin', 'System administrator role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SCS_TEST
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SCS_BRANCH_SYS_SUPPORT', 'Branch System Support', 'Branch system support for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CE_TECHNICIAN', 'Technician', 'Technician role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CHECK_SCALER', 'Check Scaler', 'Check scaler role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CLERICAL', 'Clerical', 'Clerical role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_DIST_MANAGER', 'District Manager', 'District manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_DIST_SCALING_MANAGER', 'District Scaling Manager', 'District scaling manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_INDUSTRY_SCALER', 'Industry Scaler', 'Industry scaler role for the SCS application, scoped to a forest client.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SCS_OWNER', 'Scale Site Owner', 'Scale site owner role for the SCS application, scoped to a forest client.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SCS_REGIONAL_MANAGER', 'Regional Manager', 'Regional manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_REGIONAL_SCALING_MANAGER', 'Regional Scaling Manager', 'Regional scaling manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_SYS_ADMIN', 'Admin', 'System administrator role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Add roles for SCS_PROD
INSERT INTO app_fam.fam_role (
    role_name,
    display_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
)
VALUES ('SCS_BRANCH_SYS_SUPPORT', 'Branch System Support', 'Branch system support for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CE_TECHNICIAN', 'Technician', 'Technician role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CHECK_SCALER', 'Check Scaler', 'Check scaler role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_CLERICAL', 'Clerical', 'Clerical role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_DIST_MANAGER', 'District Manager', 'District manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_DIST_SCALING_MANAGER', 'District Scaling Manager', 'District scaling manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_INDUSTRY_SCALER', 'Industry Scaler', 'Industry scaler role for the SCS application, scoped to a forest client.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SCS_OWNER', 'Scale Site Owner', 'Scale site owner role for the SCS application, scoped to a forest client.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'A', CURRENT_USER, CURRENT_DATE),
       ('SCS_REGIONAL_MANAGER', 'Regional Manager', 'Regional manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_REGIONAL_SCALING_MANAGER', 'Regional Scaling Manager', 'Regional scaling manager role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE),
       ('SCS_SYS_ADMIN', 'Admin', 'System administrator role for the SCS application.', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), 'C', CURRENT_USER, CURRENT_DATE)
;

-- Create dev, test and prod Cognito app clients for SCS
INSERT INTO app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
)
VALUES ('${client_id_dev_scs_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SCS_DEV'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_test_scs_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SCS_TEST'), CURRENT_USER, CURRENT_DATE),
       ('${client_id_prod_scs_oidc_client}', (select application_id from app_fam.fam_application where application_name = 'SCS_PROD'), CURRENT_USER, CURRENT_DATE)
;
