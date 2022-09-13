BEGIN;

-- Running upgrade V4 -> V5

COMMENT ON COLUMN app_fam.fam_application.update_user IS 'The user or proxy account that created or last updated the record.';

COMMENT ON TABLE app_fam.fam_application IS 'An application is a digital product that fulfills a  specific user goal. It can be a front-end application, a back-end API, a combination of these, or something else entirely.';

COMMENT ON COLUMN app_fam.fam_application_client.application_client_id IS 'Automatically generated key used to identify the uniqueness  of an OIDC as it corresponds to an identified client ';

COMMENT ON TABLE app_fam.fam_group IS 'A group is a collection of roles. When a group is assigned to a user, the user indirectly assumes the privileges of all the roles encompassed by the group. Groups are used to defineprofiles in order to make it easier to manage common sets of roles for users. A group can contain roles from multiple applications in order to handle the case where users typically have a certain set of privileges across multiple applications.';

COMMENT ON COLUMN app_fam.fam_user.update_user IS 'The user or proxy account that created or last updated the record.';

UPDATE alembic_version SET version_num='V5' WHERE alembic_version.version_num = 'V4';

COMMIT;

