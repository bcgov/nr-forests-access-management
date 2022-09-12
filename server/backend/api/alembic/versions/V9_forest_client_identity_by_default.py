"""forest_client Identity Column always= (as default)

   Don't use always=True because we need to insert with specific id not to be generated.
Revision ID: V9
Revises: V8
Create Date: 2022-09-12 15:32:15.162269

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision = 'V9'
down_revision = 'V8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('fam_forest_client', 'client_number_id',
        existing_type=sa.BIGINT(),
        existing_comment='Sequentially assigned number to identify a ministry client.',
        comment='Sequentially assigned number to identify a ministry client.',
        nullable=False,
        autoincrement=True,
        existing_server_default=sa.Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        server_default=sa.Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        schema='app_fam')


def downgrade() -> None:
    op.alter_column('fam_forest_client', 'client_number_id',
        existing_type=sa.BIGINT(),
        existing_comment='Sequentially assigned number to identify a ministry client.',
        comment='Sequentially assigned number to identify a ministry client.',
        nullable=False,
        autoincrement=True,
        existing_server_default=sa.Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        server_default=sa.Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        schema='app_fam')
