--
-- ER/Studio Data Architect SQL Code Generation
-- Company :      CGI
-- Project :      FAM_Model.DM1
-- Author :       Conrad Gustafson / Richard Pardo-Figueroa
--
-- Date Created : Friday, May 27, 2022 15:53:03
-- Target DBMS : PostgreSQL 10.x-12.x
--

-- 
-- TABLE: fam_application 
--

CREATE TABLE fam_application(
    application_id            numeric(10, 0)    NOT NULL,
    application_name          varchar(100)      NOT NULL,
    applicationdescription    varchar(200)      NOT NULL,
    application_client_id     numeric(10, 0),
    create_user               varchar(30)       NOT NULL,
    create_date               timestamp(6)      DEFAULT SYSDATE NOT NULL,
    update_user               varchar(30)       NOT NULL,
    update_date               timestamp(6)      DEFAULT SYSDATE,
    CONSTRAINT fam_app_pk PRIMARY KEY (application_id)
)
;



-- 
-- TABLE: fam_application_client 
--

CREATE TABLE fam_application_client(
    application_client_id    numeric(10, 0)    NOT NULL,
    cognito_client_id        varchar(32)       NOT NULL,
    create_user              varchar(30)       NOT NULL,
    create_date              timestamp(6)      DEFAULT SYSDATE NOT NULL,
    update_user              varchar(30)       NOT NULL,
    update_date              timestamp(6)      DEFAULT SYSDATE,
    CONSTRAINT fam_app_cli_pk PRIMARY KEY (application_client_id)
)
;



-- 
-- TABLE: fam_application_group_xref 
--

CREATE TABLE fam_application_group_xref(
    group_id          numeric(10, 0)    NOT NULL,
    application_id    numeric(10, 0)    NOT NULL,
    CONSTRAINT fam_app_grp_xref PRIMARY KEY (group_id, application_id)
)
;



-- 
-- TABLE: fam_forest_client 
--

CREATE TABLE fam_forest_client(
    client_number_id    numeric(10, 0)    NOT NULL,
    client_name         varchar(100)      NOT NULL,
    create_user         varchar(30)       NOT NULL,
    create_date         timestamp(6)      DEFAULT SYSDATE NOT NULL,
    update_user         varchar(30)       NOT NULL,
    update_date         timestamp(6)      DEFAULT SYSDATE,
    CONSTRAINT fam_for_cli_pk PRIMARY KEY (client_number_id)
)
;



-- 
-- TABLE: fam_group 
--

CREATE TABLE fam_group(
    group_id            numeric(10, 0)    NOT NULL,
    name                varchar(100)      NOT NULL,
    purpose             varchar(200)      NOT NULL,
    parent_group_id     numeric(10, 0),
    client_number_id    numeric(10, 0),
    create_user         varchar(30)       NOT NULL,
    create_date         timestamp(6)      DEFAULT SYSDATE NOT NULL,
    update_user         varchar(30)       NOT NULL,
    update_date         timestamp(6)      DEFAULT SYSDATE,
    CONSTRAINT fam_grp_pk PRIMARY KEY (group_id)
)
;



-- 
-- TABLE: fam_group_role_xref 
--

CREATE TABLE fam_group_role_xref(
    role_id     numeric(10, 0)    NOT NULL,
    group_id    numeric(10, 0)    NOT NULL,
    CONSTRAINT fam_grp_rle_pk PRIMARY KEY (role_id, group_id)
)
;



-- 
-- TABLE: fam_role 
--

CREATE TABLE fam_role(
    role_id             numeric(10, 0)    NOT NULL,
    role_name           varchar(100)      NOT NULL,
    role_purpose        varchar(200)      NOT NULL,
    parent_role_id      numeric(10, 0),
    application_id      numeric(10, 0)    NOT NULL,
    client_number_id    numeric(10, 0),
    create_user         varchar(30)       NOT NULL,
    create_date         timestamp(6)      DEFAULT SYSDATE NOT NULL,
    update_user         varchar(30)       NOT NULL,
    update_date         timestamp(6)      DEFAULT SYSDATE,
    CONSTRAINT pk1_1 PRIMARY KEY (role_id)
)
;



-- 
-- TABLE: fam_user 
--

CREATE TABLE fam_user(
    user_id            numeric(10, 0)    NOT NULL,
    user_type          varchar(1)        NOT NULL,
    cognito_user_id    varchar(32),
    user_name          varchar(100)      NOT NULL,
    user_guid          varchar(32)       NOT NULL,
    create_user        varchar(30)       NOT NULL,
    create_date        timestamp(6)      DEFAULT SYSDATE NOT NULL,
    update_user        varchar(30)       NOT NULL,
    update_date        timestamp(6)      DEFAULT SYSDATE,
    CONSTRAINT fam_usr_pk PRIMARY KEY (user_id)
)
;



-- 
-- TABLE: fam_user_group_xref 
--

CREATE TABLE fam_user_group_xref(
    user_id     numeric(10, 0)    NOT NULL,
    group_id    numeric(10, 0)    NOT NULL,
    CONSTRAINT fam_usr_rle_pk_1 PRIMARY KEY (user_id, group_id)
)
;



-- 
-- TABLE: fam_user_role_xref 
--

CREATE TABLE fam_user_role_xref(
    user_id    numeric(10, 0)    NOT NULL,
    role_id    numeric(10, 0)    NOT NULL,
    CONSTRAINT fam_usr_rle_pk PRIMARY KEY (user_id, role_id)
)
;



-- 
-- TABLE: fam_application 
--

ALTER TABLE fam_application ADD CONSTRAINT Reffam_application_client7 
    FOREIGN KEY (application_client_id)
    REFERENCES fam_application_client(application_client_id)
;


-- 
-- TABLE: fam_application_group_xref 
--

ALTER TABLE fam_application_group_xref ADD CONSTRAINT Reffam_group19 
    FOREIGN KEY (group_id)
    REFERENCES fam_group(group_id)
;

ALTER TABLE fam_application_group_xref ADD CONSTRAINT Reffam_application20 
    FOREIGN KEY (application_id)
    REFERENCES fam_application(application_id)
;


-- 
-- TABLE: fam_group 
--

ALTER TABLE fam_group ADD CONSTRAINT Reffam_group16 
    FOREIGN KEY (parent_group_id)
    REFERENCES fam_group(group_id)
;

ALTER TABLE fam_group ADD CONSTRAINT Reffam_forest_client25 
    FOREIGN KEY (client_number_id)
    REFERENCES fam_forest_client(client_number_id)
;


-- 
-- TABLE: fam_group_role_xref 
--

ALTER TABLE fam_group_role_xref ADD CONSTRAINT Reffam_role17 
    FOREIGN KEY (role_id)
    REFERENCES fam_role(role_id)
;

ALTER TABLE fam_group_role_xref ADD CONSTRAINT Reffam_group18 
    FOREIGN KEY (group_id)
    REFERENCES fam_group(group_id)
;


-- 
-- TABLE: fam_role 
--

ALTER TABLE fam_role ADD CONSTRAINT Reffam_application22 
    FOREIGN KEY (application_id)
    REFERENCES fam_application(application_id)
;

ALTER TABLE fam_role ADD CONSTRAINT Reffam_role23 
    FOREIGN KEY (parent_role_id)
    REFERENCES fam_role(role_id)
;

ALTER TABLE fam_role ADD CONSTRAINT Reffam_forest_client24 
    FOREIGN KEY (client_number_id)
    REFERENCES fam_forest_client(client_number_id)
;


-- 
-- TABLE: fam_user_group_xref 
--

ALTER TABLE fam_user_group_xref ADD CONSTRAINT Reffam_user29 
    FOREIGN KEY (user_id)
    REFERENCES fam_user(user_id)
;

ALTER TABLE fam_user_group_xref ADD CONSTRAINT Reffam_group30 
    FOREIGN KEY (group_id)
    REFERENCES fam_group(group_id)
;


-- 
-- TABLE: fam_user_role_xref 
--

ALTER TABLE fam_user_role_xref ADD CONSTRAINT Reffam_user10 
    FOREIGN KEY (user_id)
    REFERENCES fam_user(user_id)
;

ALTER TABLE fam_user_role_xref ADD CONSTRAINT Reffam_role12 
    FOREIGN KEY (role_id)
    REFERENCES fam_role(role_id)
;