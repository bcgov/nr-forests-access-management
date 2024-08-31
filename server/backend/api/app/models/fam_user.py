import datetime
from sqlalchemy import (
    BigInteger,
    Column,
    Identity,
    Index,
    Integer,
    String,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base


class FamUserModel(Base):
    __tablename__ = "fam_user"

    user_id = Column(
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
        comment="Automatically generated key used to identify the "
        "uniqueness of a User within the FAM Application",
    )
    user_type_code = Column(
        String(2),
        nullable=False,
        comment="Identifies which type of the user it belongs to; IDIR, BCeID etc.",
    )
    user_name = Column(String(100), nullable=False)
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
    user_guid = Column(String(32))
    business_guid = Column(
        String(32), comment="The business guid of the user if is a business bceid user."
    )
    cognito_user_id = Column(String(100))
    first_name = Column(String(50), comment="The first name of the user")
    last_name = Column(String(50), comment="The last name of the user.")
    email = Column(String(250), comment="The email of the user.")
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the " "record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )

    fam_user_role_xref = relationship("FamUserRoleXrefModel", back_populates="user")
    user_type_relation = relationship(
        "FamUserTypeModel", backref="user_relation", lazy="joined"
    )
    fam_access_control_privileges = relationship(
        "FamAccessControlPrivilegeModel", back_populates="user"
    )
    fam_user_terms_conditions = relationship(
        "FamUserTermsConditionsModel", back_populates="user"
    )

    __table_args__ = (
        PrimaryKeyConstraint("user_id", name="fam_usr_pk"),
        UniqueConstraint("user_type_code", "user_guid", name="fam_usr_uk"),
        ForeignKeyConstraint(
            [user_type_code],
            ["app_fam.fam_user_type_code.user_type_code"],
            name="reffam_user_type",
        ),
        {
            "comment": "A user is a person or system that can authenticate "
            "and then interact with an application.",
            "schema": "app_fam",
        },
    )


class FamUserTypeModel(Base):
    __tablename__ = "fam_user_type_code"

    USER_TYPE_IDIR = "I"
    USER_TYPE_BCEID = "B"

    user_type_code = Column(String(2), nullable=False, comment="user type code")

    description = Column(
        String(100),
        nullable=True,
        comment="Description of what the user_type_code represents.",
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
        PrimaryKeyConstraint("user_type_code", name="fam_user_type_code_pk"),
        {
            "comment": "A user type is a code that is associated with "
            "the user to indicate its identity provider.",
            "schema": "app_fam",
        },
    )


class FamUserTermsConditionsModel(Base):
    __tablename__ = "fam_user_terms_conditions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["app_fam.fam_user.user_id"],
            name="reffam_user_terms_conditions_user",
        ),
        PrimaryKeyConstraint(
            "user_terms_conditions_id", name="fam_user_terms_conditions_pk"
        ),
        UniqueConstraint("user_id", "version", name="fam_tc_user_version_uk"),
        Index("ix_app_fam_fam_user_terms_conditions_user_id", "user_id"),
        {
            "comment": "User Terms Conditions records identify the users who accept the "
            "terms and conditions, as well as the version of it.",
            "schema": "app_fam",
        },
    )

    user_terms_conditions_id = Column(
        BigInteger,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        comment="Automatically generated key used to identify the uniqueness of a terms and conditions acceptance record.",
    )
    user_id = Column(
        BigInteger,
        nullable=False,
        comment="Unique ID to reference and identify the user within FAM system.",
    )
    version = Column(
        String(30),
        nullable=False,
        comment="Number to identity the version of the terms and conditions the user accepted.",
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
        comment="The user or proxy account that created or last updated the record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )

    user = relationship("FamUserModel", back_populates="fam_user_terms_conditions")
