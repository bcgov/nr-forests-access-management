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
from sqlalchemy.orm import relationship
from .base import Base


class FamRoleModel(Base):
    __tablename__ = "fam_role"

    role_id = Column(
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

    application = relationship("FamApplicationModel", back_populates="fam_role")
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
    role_type_code = Column(String(2), nullable=False)
    description = Column(String(100), nullable=True)
