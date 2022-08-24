"""Columns to Nullable for fam_role table

Revision ID: 1b5a533f281f
Revises: 9f691096171b
Create Date: 2022-08-10 13:10:46.597425

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision = '1b5a533f281f'
down_revision = '9f691096171b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('fam_role', 'application_id',
                    schema='app_fam',
                    nullable=True)
        
    op.alter_column('fam_role', 'client_number_id',
                    schema='app_fam',
                    nullable=True)


def downgrade() -> None:
    op.alter_column('fam_role', 'application_id',
                    schema='app_fam',
                    nullable=False)
        
    op.alter_column('fam_role', 'client_number_id',
                    schema='app_fam',
                    nullable=False)
