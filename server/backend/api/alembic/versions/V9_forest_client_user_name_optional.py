"""forest client user_name optional

Note!: this change is to accommodate initial implementation for FAM Api that 
does not yet integrate with forest-client api. FAM frontned app is only 
accepting user input for forest-client id and FAM api backend needs to
insert forest-client record on the fly.
This field should become mandatory once FAM fully integrated with
forest-client api. 

Revision ID: V7
Revises: V6
Create Date: 2022-09-07 15:18:57.924679

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
    op.alter_column('fam_forest_client', 'client_name',
                    schema='app_fam',
                    nullable=True)


def downgrade() -> None:
    op.alter_column('fam_forest_client', 'client_name',
                    schema='app_fam',
                    nullable=False)
