"""increase user_type length

Revision ID: a186ab9c88d8
Revises: e2729cfc8443
Create Date: 2022-09-08 14:27:01.084891

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "a186ab9c88d8"
down_revision = "e2729cfc8443"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "fam_user",
        "user_type",
        schema='app_fam',
        existing_type=sa.String(length=1),
        type_=sa.String(length=10),
        existing_nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "fam_user",
        "user_type",
        schema='app_fam',
        existing_type=sa.String(length=10),
        type_=sa.String(length=1),
        existing_nullable=False
    )
