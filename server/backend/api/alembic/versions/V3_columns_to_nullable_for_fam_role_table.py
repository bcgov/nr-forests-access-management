"""Columns to Nullable for fam_role table

Revision ID: V3
Revises: V2
Create Date: 2022-08-10 13:10:46.597425

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision = 'V3'
down_revision = 'V2'
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
