"""drop composit id and use Surrogate key for user_role_xref

Revision ID: V6
Revises: V5
Create Date: 2022-09-02 16:04:41.639586

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision = 'V6'
down_revision = 'V5'
branch_labels = None
depends_on = None


def upgrade() -> None:

    # drop PrimaryKeyConstraint for "user_id" and "role_id"
    op.drop_constraint('fam_usr_rle_pk', 'fam_user_role_xref', type_='primary', schema='app_fam')

    # add new id 'user_role_xref_id' column, instead
    op.add_column('fam_user_role_xref',
       sa.Column('user_role_xref_id',
          sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), 
          sa.Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), 
          nullable=False,
          comment='Automatically generated key used to identify the uniqueness of a FamUserRoleXref within the FAM Application'),
       schema='app_fam')

    # use this id 'user_role_xref_id' column as primary key
    op.create_primary_key('fam_usr_rle_pk', 'fam_user_role_xref', ['user_role_xref_id'], schema='app_fam')
    
    # make combination of 'user_id' and 'role_id' unique
    op.create_unique_constraint('fam_usr_rle_usr_id_rle_id_uk', 'fam_user_role_xref', ['user_id', 'role_id'], schema='app_fam')


def downgrade() -> None:
    op.drop_constraint('fam_usr_rle_pk', 'fam_user_role_xref', type_='primary', schema='app_fam')

    op.drop_column('fam_user_role_xref', 'user_role_xref_id', schema='app_fam')

    op.drop_constraint('fam_usr_rle_usr_id_rle_id_uk', 'fam_user_role_xref', type_='unique', schema='app_fam')

    # recreate composit id with 'user_id' and 'role_id'
    op.create_primary_key('fam_usr_rle_pk', 'fam_user_role_xref', ['user_id', 'role_id'], schema='app_fam')
