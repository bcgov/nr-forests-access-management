BEGIN;

-- Running upgrade V7 -> V8

ALTER TABLE app_fam.fam_user_role_xref DROP CONSTRAINT fam_usr_rle_pk;

ALTER TABLE app_fam.fam_user_role_xref ADD COLUMN user_role_xref_id BIGINT GENERATED ALWAYS AS IDENTITY (INCREMENT BY 1 START WITH 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 NO CYCLE);

COMMENT ON COLUMN app_fam.fam_user_role_xref.user_role_xref_id IS 'Automatically generated key used to identify the uniqueness of a FamUserRoleXref within the FAM Application';

ALTER TABLE app_fam.fam_user_role_xref ADD CONSTRAINT fam_usr_rle_pk PRIMARY KEY (user_role_xref_id);

ALTER TABLE app_fam.fam_user_role_xref ADD CONSTRAINT fam_usr_rle_usr_id_rle_id_uk UNIQUE (user_id, role_id);

UPDATE alembic_version SET version_num='V8' WHERE alembic_version.version_num = 'V7';

COMMIT;

