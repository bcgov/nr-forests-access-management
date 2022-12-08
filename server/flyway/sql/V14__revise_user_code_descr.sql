BEGIN;

-- Running upgrade V13 -> V14

UPDATE app_fam.fam_user_type_code SET description = 'BCEID' WHERE user_type_code = 'B';

UPDATE app_fam.fam_user_type_code SET description = 'IDIR' WHERE user_type_code = 'I';

UPDATE alembic_version SET version_num='V14' WHERE alembic_version.version_num = 'V13';

COMMIT;

