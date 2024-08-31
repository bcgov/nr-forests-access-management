import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKeyConstraint,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from api.app.models import Base


class FamUserRoleXrefModel(Base):
    __tablename__ = "fam_user_role_xref"
    __table_args__ = (
        ForeignKeyConstraint(
            ["role_id"], ["app_fam.fam_role.role_id"], name="reffam_role12"
        ),
        ForeignKeyConstraint(
            ["user_id"], ["app_fam.fam_user.user_id"], name="reffam_user10"
        ),
        PrimaryKeyConstraint("user_role_xref_id", name="fam_usr_rle_xrf_pk"),
        UniqueConstraint("user_id", "role_id", name="fam_usr_rle_usr_id_rle_id_uk"),
        {
            "comment": "User Role Xref is a cross-reference object that allows for the identification of Roles assigned to a user, as well as the users that belong to a given Role",
            "schema": "app_fam",
        },  # reference: https://docs.sqlalchemy.org/en/14/orm/declarative_tables.html#orm-declarative-table-configuration
    )

    user_role_xref_id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        comment="Automatically generated key used to identify the uniqueness "
        "of a FamUserRoleXref within the FAM Application",
    )

    user_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Automatically generated key used to identify the uniqueness "
        "of a User within the FAM Application",
    )
    role_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Automatically generated key used to identify the uniqueness "
        "of a Role within the FAM Application",
    )
    create_user = Column(
        String(100),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated "
        "the record. ",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created or last updated.",
    )

    role = relationship("FamRoleModel", back_populates="fam_user_role_xref", lazy="joined")
    user = relationship("FamUserModel", back_populates="fam_user_role_xref", lazy="joined")
