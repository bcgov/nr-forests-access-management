import datetime
from typing import List
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
from sqlalchemy.orm import Mapped, relationship
from api.app.models import Base, FamAccessControlPrivilegeModel, FamUserTermsConditionsModel


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
        default=datetime.datetime.now(datetime.UTC),
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
        onupdate=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created or last updated.",
    )

    fam_user_role_xref = relationship("FamUserRoleXref", back_populates="user")
    user_type_relation = relationship(
        "FamUserType", backref="user_relation", lazy="joined"
    )
    fam_access_control_privileges: Mapped[List[FamAccessControlPrivilegeModel]] = (
        relationship("FamAccessControlPrivilege", back_populates="user")
    )
    fam_user_terms_conditions: Mapped[FamUserTermsConditionsModel] = relationship(
        "FamUserTermsConditions", back_populates="user"
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

    def __str__(self):
        return f"FamUser({self.user_id}, {self.user_name}, {self.user_type_code})"
