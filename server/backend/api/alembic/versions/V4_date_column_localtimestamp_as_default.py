"""Date column 'LOCALTIMESTAMP' as default
This change is only on 'create_date' and 'update_date' columns.
Affected tables: 'fam_application, fam_forest_client, fam_user, fam_application_client, fam_group,
                  fam_role, fam_application_group_xref, fam_group_role_xref, fam_user_group_xref,
                  fam_user_role_xref'

Revision ID: V4
Revises: V3
Create Date: 2022-08-11 12:46:15.364661

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'V4'
down_revision = 'V3'
branch_labels = None
depends_on = None


def upgrade() -> None:

    # fam_application
    op.alter_column('fam_application', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_application', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_forest_client
    op.alter_column('fam_forest_client', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_forest_client', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_user
    op.alter_column('fam_user', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_user', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_application_client
    op.alter_column('fam_application_client', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_application_client', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_group
    op.alter_column('fam_group', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_group', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_role
    op.alter_column('fam_role', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_role', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_application_group_xref
    op.alter_column('fam_application_group_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_application_group_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_group_role_xref
    op.alter_column('fam_group_role_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_group_role_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_user_group_xref
    op.alter_column('fam_user_group_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_user_group_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))

    # fam_user_role_xref
    op.alter_column('fam_user_role_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))
    op.alter_column('fam_user_role_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('LOCALTIMESTAMP'))


def downgrade() -> None:

    # fam_application
    op.alter_column('fam_application', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_application', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_forest_client
    op.alter_column('fam_forest_client', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_forest_client', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_user
    op.alter_column('fam_user', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_user', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_application_client
    op.alter_column('fam_application_client', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_application_client', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_group
    op.alter_column('fam_group', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_group', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_role
    op.alter_column('fam_role', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_role', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_application_group_xref
    op.alter_column('fam_application_group_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_application_group_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_group_role_xref
    op.alter_column('fam_group_role_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_group_role_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_user_group_xref
    op.alter_column('fam_user_group_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_user_group_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))

    # fam_user_role_xref
    op.alter_column('fam_user_role_xref', 'create_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
    op.alter_column('fam_user_role_xref', 'update_date',
                    schema='app_fam',
                    server_default=sa.text('CURRENT_DATE'))
