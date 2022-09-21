BEGIN;

-- Running upgrade V5 -> V6

ALTER TABLE app_fam.fam_role ADD COLUMN role_type VARCHAR(15) NOT NULL;

COMMENT ON COLUMN app_fam.fam_role.role_type IS 'Identifies if the role is a parent or child role.  Users should only be assigned to roles where role_type=child';

UPDATE alembic_version SET version_num='V6' WHERE alembic_version.version_num = 'V5';

COMMIT;

