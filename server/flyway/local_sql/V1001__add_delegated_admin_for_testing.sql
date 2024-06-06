-- create user for running test, test for the security check for delegated admin grant/remove access

-- create two business bceid users from the same organization, one from different organization
INSERT INTO app_fam.fam_user (
    user_name,
    user_type_code,
    cognito_user_id,
    business_guid,
    create_user
)
VALUES
('TEST-3-LOAD-CHILD-1','B','test-bceidbusiness_bda2a1e212244dc2b9f9522057mangledc58bbb@bceidbusiness', 'E7C0431DA55D4ACA9FA901EE2C91CB3B', CURRENT_USER),
('LOAD-3-TEST', 'B', 'test-bceidbusiness_532905de0aa24923ae535428mangledf171bf13@bceidbusiness', 'E7C0431DA55D4ACA9FA901EE2C91CB3B', CURRENT_USER),
('LOAD-4-TEST', 'B', 'test-bceidbusiness_b5251dbe95724894aa698043mangled099a4de2@bceidbusiness ', 'B1323E832A4A4947B50367EF4A4F79DE', CURRENT_USER);

-- add user_guid for TEST-3-LOAD-CHILD-1, as we use it as requester for tests
UPDATE app_fam.fam_user
SET user_guid = 'BDA2A1E212244DC2B9F9522057C58BBB'
WHERE user_name = 'TEST-3-LOAD-CHILD-1';


-- add PTOLLEST as delegated admin to manage FOM DEV role FOM_REVIEWER
-- add TEST-3-LOAD-CHILD-1 as delegated admin to manage FOM DEV role FOM_REVIEWER
INSERT INTO app_fam.fam_access_control_privilege (
    user_id,
    role_id,
    create_user
)
VALUES
(
    (select user_id from app_fam.fam_user where user_name='PTOLLEST' and user_type_code='I'),
    (select role_id from app_fam.fam_role where role_name='FOM_REVIEWER' and application_id=(select application_id from app_fam.fam_application where application_name = 'FOM_DEV')),
    CURRENT_USER
),
(
    (select user_id from app_fam.fam_user where user_name='TEST-3-LOAD-CHILD-1' and user_type_code='B'),
    (select role_id from app_fam.fam_role where role_name='FOM_REVIEWER' and application_id=(select application_id from app_fam.fam_application where application_name = 'FOM_DEV')),
    CURRENT_USER
);


-- create a forest client number
INSERT INTO app_fam.fam_forest_client (
    forest_client_number,
    create_user
)
VALUES (
    '00001018',
    CURRENT_USER
);


-- create a chile role FOM_SUBMITTER_00001018
INSERT INTO app_fam.fam_role (
    role_name,
    role_purpose,
    parent_role_id,
    application_id,
    client_number_id,
    role_type_code,
    create_user
)
VALUES (
    'FOM_SUBMITTER_00001018',
    'Provides the privilege to submit a FOM (on behalf of a specific forest client) for 00001018',
    (select role_id from app_fam.fam_role where role_name='FOM_SUBMITTER' and application_id=(select application_id from app_fam.fam_application where application_name = 'FOM_DEV')),
    (select application_id from app_fam.fam_application where application_name = 'FOM_DEV'),
    (select client_number_id from app_fam.fam_forest_client where forest_client_number = '00001018'),
    'C',
    CURRENT_USER
);

-- add PTOLLEST as delegated admin to manage FOM DEV role FOM_SUBMITTER with forest client number 00001018
-- add TEST-3-LOAD-CHILD-1 as delegated admin to manage FOM DEV role FOM_SUBMITTER with forest client number 00001018
INSERT INTO app_fam.fam_access_control_privilege (
    user_id,
    role_id,
    create_user
)
VALUES
(
    (select user_id from app_fam.fam_user where user_name='PTOLLEST' and user_type_code='I'),
    (select role_id from app_fam.fam_role where role_name='FOM_SUBMITTER_00001018' and application_id=(select application_id from app_fam.fam_application where application_name = 'FOM_DEV')),
    CURRENT_USER
),
(
    (select user_id from app_fam.fam_user where user_name='TEST-3-LOAD-CHILD-1' and user_type_code='B'),
    (select role_id from app_fam.fam_role where role_name='FOM_SUBMITTER_00001018' and application_id=(select application_id from app_fam.fam_application where application_name = 'FOM_DEV')),
    CURRENT_USER
);
