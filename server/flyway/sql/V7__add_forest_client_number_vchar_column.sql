BEGIN;

-- Running upgrade V6 -> V7

ALTER TABLE app_fam.fam_forest_client ADD COLUMN forest_client_number VARCHAR NOT NULL;

COMMENT ON COLUMN app_fam.fam_forest_client.forest_client_number IS 'Id number as String from external Forest Client source(api/table) that identifies the Forest Client.';

ALTER TABLE app_fam.fam_forest_client ADD CONSTRAINT fam_for_cli_num_uk UNIQUE (forest_client_number);

CREATE INDEX ix_app_fam_fam_forest_client_client_name ON app_fam.fam_forest_client (client_name);

CREATE INDEX ix_app_fam_fam_forest_client_forest_client_number ON app_fam.fam_forest_client (forest_client_number);

UPDATE alembic_version SET version_num='V7' WHERE alembic_version.version_num = 'V6';

COMMIT;

