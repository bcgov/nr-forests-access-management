import datetime
from sqlalchemy import (
    BigInteger,
    Column,
    Identity,
    Integer,
    String,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship, Mapped

from api.app.models.fam_application import FamApplicationModel
from .base import Base


class FamRoleModel(Base):
    __tablename__ = "fam_role"

    role_id = Column(
        # Use '.with_variant' for sqlite as it does not recognize BigInteger
        # Ref: 	https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#allowing-autoincrement-behavior-sqlalchemy-types-other-than-integer-integer
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
        "of a Role within the FAM Application",
    )
    role_name = Column(String(100), nullable=False)
    role_purpose = Column(String(300), nullable=True)
    display_name = Column(String(100), nullable=True)
    application_id = Column(BigInteger, nullable=False, index=True)
    client_number_id = Column(
        BigInteger,
        nullable=True,
        index=True,
        comment="Sequentially assigned number to identify a ministry client.",
    )
    create_user = Column(
        String(100),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created.",
    )
    parent_role_id = Column(
        BigInteger,
        nullable=True,
        index=True,
        comment="Automatically generated key used to identify the uniqueness "
        + "of a Role within the FAM Application",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )
    role_type_code = Column(
        String(2),
        nullable=False,
        comment="Identifies if the role is an abstract or concrete role. "
        + "Users should only be assigned to roles where "
        + "role_type=concrete",
    )

    application: Mapped[FamApplicationModel] = relationship(
        "FamApplicationModel", back_populates="fam_role"
    )
    client_number = relationship(
        "FamForestClientModel", back_populates="fam_role", lazy="joined"
    )
    parent_role = relationship(
        "FamRoleModel", remote_side=[role_id], back_populates="parent_role_reverse"
    )
    parent_role_reverse = relationship(
        "FamRoleModel", remote_side=[parent_role_id], back_populates="parent_role"
    )
    fam_user_role_xref = relationship("FamUserRoleXrefModel", back_populates="role")
    role_type_relation = relationship("FamRoleTypeModel", backref="role_relation")
    fam_access_control_privilege = relationship(
        "FamAccessControlPrivilegeModel", back_populates="role"
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["application_id"],
            ["app_fam.fam_application.application_id"],
            name="reffam_application22",
        ),
        ForeignKeyConstraint(
            ["client_number_id"],
            ["app_fam.fam_forest_client.client_number_id"],
            name="reffam_forest_client24",
        ),
        ForeignKeyConstraint(
            ["parent_role_id"], ["app_fam.fam_role.role_id"], name="reffam_role23"
        ),
        PrimaryKeyConstraint("role_id", name="fam_rle_pk"),
        UniqueConstraint("role_name", "application_id", name="fam_rlnm_app_uk"),
        ForeignKeyConstraint(
            [role_type_code],
            ["app_fam.fam_role_type.role_type_code"],
            name="reffam_role_type",
        ),
        {
            "comment": "A role is a qualifier that can be assigned to a user "
            "in order to identify a privilege within the context of an "
            "application.",
            "schema": "app_fam",
        },
    )


class FamRoleTypeModel(Base):
    __tablename__ = "fam_role_type"

    # ROLE_TYPE_ABSTRACT = 'A'
    # ROLE_TYPE_CONCRETE = 'C'

    role_type_code = Column(String(2), nullable=False, comment="role type code")

    description = Column(
        String(100),
        nullable=True,
        comment="Description of what the role_type_code represents",
    )

    effective_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="The date and time the code was effective.",
    )

    expiry_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=True,
        default=None,
        comment="The date and time the code expired.",
    )

    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )

    __table_args__ = (
        PrimaryKeyConstraint("role_type_code", name="fam_role_type_code_pk"),
        # CheckConstraint(role_type_code.in_(['C', 'A'])),
        {
            "comment": "A role type is a code that is associated with roles "
            "that will influence what can be associate with a role.  At time "
            "of implementation an abstract role can only have other roles "
            "related to it, while a concrete role can only have users "
            "associated with it",
            "schema": "app_fam",
        },
    )

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
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated "
        "the record. ",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )

    role = relationship("FamRoleModel", back_populates="fam_user_role_xref", lazy="joined")
    user = relationship("FamUserModel", back_populates="fam_user_role_xref", lazy="joined")
