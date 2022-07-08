--
-- ER/Studio Data Architect SQL Code Generation
-- Company :      CGI
-- Project :      FAM_Model.DM1
-- Author :       Conrad Gustafson / Richard Pardo-Figueroa
--
-- Date Created : Thursday, July 07, 2022 17:38:44
-- Target DBMS : PostgreSQL 10.x-12.x
--

-- 
-- SCHEMA: APP_FAM 
--

CREATE SCHEMA IF NOT EXISTS "APP_FAM";

-- 
-- USER: FAM_PROXY_API 
--

CREATE USER "FAM_PROXY_API";

-- GRANT FAM_ADMIN_ROLE TO FAM_PROXY_API;

GRANT SELECT, UPDATE, DELETE, INSERT ON ALL TABLES IN SCHEMA "APP_FAM" TO "FAM_PROXY_API";

-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION" 
--

CREATE TABLE "APP_FAM"."FAM_APPLICATION"(
    "APPLICATION_ID"           bigint            NOT NULL,
    "APPLICATION_NAME"         varchar(100)      NOT NULL,
    "APPLICATION_DESCRIPTION"  varchar(200)      NOT NULL,
    "APPLICATION_CLIENT_ID"    bigint,
    "CREATE_USER"              varchar(30)       NOT NULL,
    "CREATE_DATE"              timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"              varchar(30),
    "UPDATE_DATE"              timestamp(6)      DEFAULT CURRENT_DATE
)
;
ALTER TABLE "APP_FAM"."FAM_APPLICATION" ALTER COLUMN "APPLICATION_ID" ADD GENERATED ALWAYS AS IDENTITY;

COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION"."APPLICATION_ID" IS 'Automatically generated key used to identify the uniqueness of an Application registered under FAM'
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION"."APPLICATION_CLIENT_ID" IS 'Automatically generated key used to identify the uniqueness of an OIDC as it corresponds to an identified client '
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;
COMMENT ON TABLE "APP_FAM"."FAM_APPLICATION" IS 'An application is a digital product that fulfills a specific user goal. It can be a front-end application, a back-end API, a combination of these, or something else entirely.'
;

-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION_CLIENT" 
--

CREATE TABLE "APP_FAM"."FAM_APPLICATION_CLIENT"(
    "APPLICATION_CLIENT_ID"  bigint            NOT NULL,
    "COGNITO_CLIENT_ID"      varchar(32)       NOT NULL,
    "CREATE_USER"            varchar(30)       NOT NULL,
    "CREATE_DATE"            timestamp(6)      NOT NULL,
    "UPDATE_USER"            varchar(30),
    "UPDATE_DATE"            varchar(9)        DEFAULT CURRENT_DATE
)
;
ALTER TABLE "APP_FAM"."FAM_APPLICATION_CLIENT" ALTER COLUMN "APPLICATION_CLIENT_ID" ADD GENERATED ALWAYS AS IDENTITY;

COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_CLIENT"."APPLICATION_CLIENT_ID" IS 'Automatically generated key used to identify the uniqueness of an OIDC as it corresponds to an identified client '
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_CLIENT"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_CLIENT"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_CLIENT"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_CLIENT"."UPDATE_DATE" IS 'ZIP code.'
;
COMMENT ON TABLE "APP_FAM"."FAM_APPLICATION_CLIENT" IS 'FAM needs to know the OIDC client ID in order to match to an application. The relationship between OIDC client and application is many-to-one because sometimes there is more than one OIDC client for an application and it is convenient to be able to configure the authorization once (at the application level) and re-use it (at the OIDC level).'
;

-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION_GROUP_XREF" 
--

CREATE TABLE "APP_FAM"."FAM_APPLICATION_GROUP_XREF"(
    "GROUP_ID"        bigint            NOT NULL,
    "APPLICATION_ID"  bigint            NOT NULL,
    "CREATE_USER"     varchar(30)       NOT NULL,
    "CREATE_DATE"     timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"     varchar(30),
    "UPDATE_DATE"     timestamp(6)      DEFAULT CURRENT_DATE
)
;



COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_GROUP_XREF"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_GROUP_XREF"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_GROUP_XREF"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_APPLICATION_GROUP_XREF"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;

-- 
-- TABLE: "APP_FAM"."FAM_FOREST_CLIENT" 
--

CREATE TABLE "APP_FAM"."FAM_FOREST_CLIENT"(
    "CLIENT_NUMBER_ID"  bigint            NOT NULL,
    "CLIENT_NAME"       varchar(100)      NOT NULL,
    "CREATE_USER"       varchar(30)       NOT NULL,
    "CREATE_DATE"       timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"       varchar(30),
    "UPDATE_DATE"       timestamp(6)      DEFAULT CURRENT_DATE
)
;
ALTER TABLE "APP_FAM"."FAM_FOREST_CLIENT" ALTER COLUMN "CLIENT_NUMBER_ID" ADD GENERATED ALWAYS AS IDENTITY;

COMMENT ON COLUMN "APP_FAM"."FAM_FOREST_CLIENT"."CLIENT_NUMBER_ID" IS 'Sequentially assigned number to identify a ministry client.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_FOREST_CLIENT"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_FOREST_CLIENT"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_FOREST_CLIENT"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_FOREST_CLIENT"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;
COMMENT ON TABLE "APP_FAM"."FAM_FOREST_CLIENT" IS 'A forest client is a business, individual, or agency that is identified as an entity that a user can have a privilege "on behalf of".'
;

-- 
-- TABLE: "APP_FAM"."FAM_GROUP" 
--

CREATE TABLE "APP_FAM"."FAM_GROUP"(
    "GROUP_ID"          bigint            NOT NULL,
    "NAME"              varchar(100)      NOT NULL,
    "PURPOSE"           varchar(200)      NOT NULL,
    "PARENT_GROUP_ID"   bigint,
    "CLIENT_NUMBER_ID"  bigint,
    "CREATE_USER"       varchar(30)       NOT NULL,
    "CREATE_DATE"       timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"       varchar(30),
    "UPDATE_DATE"       timestamp(6)      DEFAULT CURRENT_DATE
)
;
ALTER TABLE "APP_FAM"."FAM_GROUP" ALTER COLUMN "GROUP_ID" ADD GENERATED ALWAYS AS IDENTITY;

COMMENT ON COLUMN "APP_FAM"."FAM_GROUP"."CLIENT_NUMBER_ID" IS 'Sequentially assigned number to identify a ministry client.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;
COMMENT ON TABLE "APP_FAM"."FAM_GROUP" IS 'A group is a collection of roles. When a group is assigned to a user, the user indirectly assumes the privileges of all the roles encompassed by the group. Groups are used to define profiles in order to make it easier to manage common sets of roles for users. A group can contain roles from multiple applications in order to handle the case where users typically have a certain set of privileges across multiple applications.'
;

-- 
-- TABLE: "APP_FAM"."FAM_GROUP_ROLE_XREF" 
--

CREATE TABLE "APP_FAM"."FAM_GROUP_ROLE_XREF"(
    "ROLE_ID"      bigint            NOT NULL,
    "GROUP_ID"     bigint            NOT NULL,
    "CREATE_USER"  varchar(30)       NOT NULL,
    "CREATE_DATE"  timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"  varchar(30),
    "UPDATE_DATE"  timestamp(6)      DEFAULT CURRENT_DATE
)
;



COMMENT ON COLUMN "APP_FAM"."FAM_GROUP_ROLE_XREF"."ROLE_ID" IS 'Automatically generated key used to identify the uniqueness of a Role within the FAM Application'
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP_ROLE_XREF"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP_ROLE_XREF"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP_ROLE_XREF"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_GROUP_ROLE_XREF"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;

-- 
-- TABLE: "APP_FAM"."FAM_ROLE" 
--

CREATE TABLE "APP_FAM"."FAM_ROLE"(
    "ROLE_ID"           bigint            NOT NULL,
    "ROLE_NAME"         varchar(100)      NOT NULL,
    "ROLE_PURPOSE"      varchar(200)      NOT NULL,
    "PARENT_ROLE_ID"    bigint,
    "APPLICATION_ID"    bigint            NOT NULL,
    "CLIENT_NUMBER_ID"  bigint,
    "CREATE_USER"       varchar(30)       NOT NULL,
    "CREATE_DATE"       timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"       varchar(30),
    "UPDATE_DATE"       timestamp(6)      DEFAULT CURRENT_DATE
)
;
ALTER TABLE "APP_FAM"."FAM_ROLE" ALTER COLUMN "ROLE_ID" ADD GENERATED ALWAYS AS IDENTITY;

COMMENT ON COLUMN "APP_FAM"."FAM_ROLE"."ROLE_ID" IS 'Automatically generated key used to identify the uniqueness of a Role within the FAM Application'
;
COMMENT ON COLUMN "APP_FAM"."FAM_ROLE"."PARENT_ROLE_ID" IS 'Automatically generated key used to identify the uniqueness of a Role within the FAM Application'
;
COMMENT ON COLUMN "APP_FAM"."FAM_ROLE"."CLIENT_NUMBER_ID" IS 'Sequentially assigned number to identify a ministry client.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_ROLE"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_ROLE"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_ROLE"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_ROLE"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;
COMMENT ON TABLE "APP_FAM"."FAM_ROLE" IS 'A role is a qualifier that can be assigned to a user in order to identify a privilege within the context of an application.'
;

-- 
-- TABLE: "APP_FAM"."FAM_USER" 
--

CREATE TABLE "APP_FAM"."FAM_USER"(
    "USER_ID"          bigint            NOT NULL,
    "USER_TYPE"        varchar(1)        NOT NULL,
    "COGNITO_USER_ID"  varchar(32),
    "USER_NAME"        varchar(100)      NOT NULL,
    "USER_GUID"        varchar(32)       NOT NULL,
    "CREATE_USER"      varchar(30)       NOT NULL,
    "CREATE_DATE"      timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"      varchar(30),
    "UPDATE_DATE"      timestamp(6)      DEFAULT CURRENT_DATE
)
;
ALTER TABLE "APP_FAM"."FAM_USER" ALTER COLUMN "USER_ID" ADD GENERATED ALWAYS AS IDENTITY;

COMMENT ON COLUMN "APP_FAM"."FAM_USER"."USER_ID" IS 'Automatically generated key used to identify the uniqueness of a User within the FAM Application'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;
COMMENT ON TABLE "APP_FAM"."FAM_USER" IS 'A user is a person or system that can authenticate and then interact with an application.'
;

-- 
-- TABLE: "APP_FAM"."FAM_USER_GROUP_XREF" 
--

CREATE TABLE "APP_FAM"."FAM_USER_GROUP_XREF"(
    "USER_ID"      bigint            NOT NULL,
    "GROUP_ID"     bigint            NOT NULL,
    "CREATE_USER"  varchar(30)       NOT NULL,
    "CREATE_DATE"  timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"  varchar(30),
    "UPDATE_DATE"  timestamp(6)      DEFAULT CURRENT_DATE
)
;



COMMENT ON COLUMN "APP_FAM"."FAM_USER_GROUP_XREF"."USER_ID" IS 'Automatically generated key used to identify the uniqueness of a User within the FAM Application'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_GROUP_XREF"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_GROUP_XREF"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_GROUP_XREF"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_GROUP_XREF"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;
COMMENT ON TABLE "APP_FAM"."FAM_USER_GROUP_XREF" IS 'User Group Xref is a cross-reference object that allows for the identification of Groups assigned to a user, as well as the users that belong to a given Group'
;

-- 
-- TABLE: "APP_FAM"."FAM_USER_ROLE_XREF" 
--

CREATE TABLE "APP_FAM"."FAM_USER_ROLE_XREF"(
    "USER_ID"      bigint            NOT NULL,
    "ROLE_ID"      bigint            NOT NULL,
    "CREATE_USER"  varchar(30)       NOT NULL,
    "CREATE_DATE"  timestamp(6)      DEFAULT CURRENT_DATE NOT NULL,
    "UPDATE_USER"  varchar(30),
    "UPDATE_DATE"  timestamp(6)      DEFAULT CURRENT_DATE
)
;



COMMENT ON COLUMN "APP_FAM"."FAM_USER_ROLE_XREF"."USER_ID" IS 'Automatically generated key used to identify the uniqueness of a User within the FAM Application'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_ROLE_XREF"."ROLE_ID" IS 'Automatically generated key used to identify the uniqueness of a Role within the FAM Application'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_ROLE_XREF"."CREATE_USER" IS 'The user or proxy account that created the record.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_ROLE_XREF"."CREATE_DATE" IS 'The date and time the record was created.'
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_ROLE_XREF"."UPDATE_USER" IS 'The user or proxy account that created or last updated the record. '
;
COMMENT ON COLUMN "APP_FAM"."FAM_USER_ROLE_XREF"."UPDATE_DATE" IS 'The date and time the record was created or last updated.'
;
COMMENT ON TABLE "APP_FAM"."FAM_USER_ROLE_XREF" IS 'User Role Xref is a cross-reference object that allows for the identification of Roles assigned to a user, as well as the users that belong to a given Role'
;

-- 
-- INDEX: "Ref67" 
--

CREATE INDEX "Ref67" ON "APP_FAM"."FAM_APPLICATION"("APPLICATION_CLIENT_ID")
;
-- 
-- INDEX: "Ref219" 
--

CREATE INDEX "Ref219" ON "APP_FAM"."FAM_APPLICATION_GROUP_XREF"("GROUP_ID")
;
-- 
-- INDEX: "Ref720" 
--

CREATE INDEX "Ref720" ON "APP_FAM"."FAM_APPLICATION_GROUP_XREF"("APPLICATION_ID")
;
-- 
-- INDEX: "Ref216" 
--

CREATE INDEX "Ref216" ON "APP_FAM"."FAM_GROUP"("PARENT_GROUP_ID")
;
-- 
-- INDEX: "Ref425" 
--

CREATE INDEX "Ref425" ON "APP_FAM"."FAM_GROUP"("CLIENT_NUMBER_ID")
;
-- 
-- INDEX: "Ref1217" 
--

CREATE INDEX "Ref1217" ON "APP_FAM"."FAM_GROUP_ROLE_XREF"("ROLE_ID")
;
-- 
-- INDEX: "Ref218" 
--

CREATE INDEX "Ref218" ON "APP_FAM"."FAM_GROUP_ROLE_XREF"("GROUP_ID")
;
-- 
-- INDEX: "Ref722" 
--

CREATE INDEX "Ref722" ON "APP_FAM"."FAM_ROLE"("APPLICATION_ID")
;
-- 
-- INDEX: "Ref1223" 
--

CREATE INDEX "Ref1223" ON "APP_FAM"."FAM_ROLE"("PARENT_ROLE_ID")
;
-- 
-- INDEX: "Ref424" 
--

CREATE INDEX "Ref424" ON "APP_FAM"."FAM_ROLE"("CLIENT_NUMBER_ID")
;
-- 
-- INDEX: "Ref329" 
--

CREATE INDEX "Ref329" ON "APP_FAM"."FAM_USER_GROUP_XREF"("USER_ID")
;
-- 
-- INDEX: "Ref230" 
--

CREATE INDEX "Ref230" ON "APP_FAM"."FAM_USER_GROUP_XREF"("GROUP_ID")
;
-- 
-- INDEX: "Ref310" 
--

CREATE INDEX "Ref310" ON "APP_FAM"."FAM_USER_ROLE_XREF"("USER_ID")
;
-- 
-- INDEX: "Ref1212" 
--

CREATE INDEX "Ref1212" ON "APP_FAM"."FAM_USER_ROLE_XREF"("ROLE_ID")
;
-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION" 
--

ALTER TABLE "APP_FAM"."FAM_APPLICATION" ADD 
    CONSTRAINT FAM_APP_PK PRIMARY KEY ("APPLICATION_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION_CLIENT" 
--

ALTER TABLE "APP_FAM"."FAM_APPLICATION_CLIENT" ADD 
    CONSTRAINT FAM_APP_CLI_PK PRIMARY KEY ("APPLICATION_CLIENT_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION_GROUP_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_APPLICATION_GROUP_XREF" ADD 
    CONSTRAINT FAM_APP_GRP_XREF PRIMARY KEY ("GROUP_ID", "APPLICATION_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_FOREST_CLIENT" 
--

ALTER TABLE "APP_FAM"."FAM_FOREST_CLIENT" ADD 
    CONSTRAINT FAM_FOR_CLI_PK PRIMARY KEY ("CLIENT_NUMBER_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_GROUP" 
--

ALTER TABLE "APP_FAM"."FAM_GROUP" ADD 
    CONSTRAINT FAM_GRP_PK PRIMARY KEY ("GROUP_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_GROUP_ROLE_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_GROUP_ROLE_XREF" ADD 
    CONSTRAINT FAM_GRP_RLE_PK PRIMARY KEY ("ROLE_ID", "GROUP_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_ROLE" 
--

ALTER TABLE "APP_FAM"."FAM_ROLE" ADD 
    CONSTRAINT PK1_1 PRIMARY KEY ("ROLE_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_USER" 
--

ALTER TABLE "APP_FAM"."FAM_USER" ADD 
    CONSTRAINT FAM_USR_PK PRIMARY KEY ("USER_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_USER_GROUP_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_USER_GROUP_XREF" ADD 
    CONSTRAINT FAM_USR_RLE_PK_1 PRIMARY KEY ("USER_ID", "GROUP_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_USER_ROLE_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_USER_ROLE_XREF" ADD 
    CONSTRAINT FAM_USR_RLE_PK PRIMARY KEY ("USER_ID", "ROLE_ID")
;

-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION" 
--

ALTER TABLE "APP_FAM"."FAM_APPLICATION" ADD CONSTRAINT RefFAM_APPLICATION_CLIENT7 
    FOREIGN KEY ("APPLICATION_CLIENT_ID")
    REFERENCES "APP_FAM"."FAM_APPLICATION_CLIENT"("APPLICATION_CLIENT_ID")
;


-- 
-- TABLE: "APP_FAM"."FAM_APPLICATION_GROUP_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_APPLICATION_GROUP_XREF" ADD CONSTRAINT RefFAM_GROUP19 
    FOREIGN KEY ("GROUP_ID")
    REFERENCES "APP_FAM"."FAM_GROUP"("GROUP_ID")
;

ALTER TABLE "APP_FAM"."FAM_APPLICATION_GROUP_XREF" ADD CONSTRAINT RefFAM_APPLICATION20 
    FOREIGN KEY ("APPLICATION_ID")
    REFERENCES "APP_FAM"."FAM_APPLICATION"("APPLICATION_ID")
;


-- 
-- TABLE: "APP_FAM"."FAM_GROUP" 
--

ALTER TABLE "APP_FAM"."FAM_GROUP" ADD CONSTRAINT RefFAM_GROUP16 
    FOREIGN KEY ("PARENT_GROUP_ID")
    REFERENCES "APP_FAM"."FAM_GROUP"("GROUP_ID")
;

ALTER TABLE "APP_FAM"."FAM_GROUP" ADD CONSTRAINT RefFAM_FOREST_CLIENT25 
    FOREIGN KEY ("CLIENT_NUMBER_ID")
    REFERENCES "APP_FAM"."FAM_FOREST_CLIENT"("CLIENT_NUMBER_ID")
;


-- 
-- TABLE: "APP_FAM"."FAM_GROUP_ROLE_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_GROUP_ROLE_XREF" ADD CONSTRAINT RefFAM_ROLE17 
    FOREIGN KEY ("ROLE_ID")
    REFERENCES "APP_FAM"."FAM_ROLE"("ROLE_ID")
;

ALTER TABLE "APP_FAM"."FAM_GROUP_ROLE_XREF" ADD CONSTRAINT RefFAM_GROUP18 
    FOREIGN KEY ("GROUP_ID")
    REFERENCES "APP_FAM"."FAM_GROUP"("GROUP_ID")
;


-- 
-- TABLE: "APP_FAM"."FAM_ROLE" 
--

ALTER TABLE "APP_FAM"."FAM_ROLE" ADD CONSTRAINT RefFAM_APPLICATION22 
    FOREIGN KEY ("APPLICATION_ID")
    REFERENCES "APP_FAM"."FAM_APPLICATION"("APPLICATION_ID")
;

ALTER TABLE "APP_FAM"."FAM_ROLE" ADD CONSTRAINT RefFAM_ROLE23 
    FOREIGN KEY ("PARENT_ROLE_ID")
    REFERENCES "APP_FAM"."FAM_ROLE"("ROLE_ID")
;

ALTER TABLE "APP_FAM"."FAM_ROLE" ADD CONSTRAINT RefFAM_FOREST_CLIENT24 
    FOREIGN KEY ("CLIENT_NUMBER_ID")
    REFERENCES "APP_FAM"."FAM_FOREST_CLIENT"("CLIENT_NUMBER_ID")
;


-- 
-- TABLE: "APP_FAM"."FAM_USER_GROUP_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_USER_GROUP_XREF" ADD CONSTRAINT RefFAM_USER29 
    FOREIGN KEY ("USER_ID")
    REFERENCES "APP_FAM"."FAM_USER"("USER_ID")
;

ALTER TABLE "APP_FAM"."FAM_USER_GROUP_XREF" ADD CONSTRAINT RefFAM_GROUP30 
    FOREIGN KEY ("GROUP_ID")
    REFERENCES "APP_FAM"."FAM_GROUP"("GROUP_ID")
;


-- 
-- TABLE: "APP_FAM"."FAM_USER_ROLE_XREF" 
--

ALTER TABLE "APP_FAM"."FAM_USER_ROLE_XREF" ADD CONSTRAINT RefFAM_USER10 
    FOREIGN KEY ("USER_ID")
    REFERENCES "APP_FAM"."FAM_USER"("USER_ID")
;

ALTER TABLE "APP_FAM"."FAM_USER_ROLE_XREF" ADD CONSTRAINT RefFAM_ROLE12 
    FOREIGN KEY ("ROLE_ID")
    REFERENCES "APP_FAM"."FAM_ROLE"("ROLE_ID")
;


