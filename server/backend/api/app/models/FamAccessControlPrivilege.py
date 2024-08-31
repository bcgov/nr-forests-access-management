import datetime
from typing import List

from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKeyConstraint,
    Identity,
    Index,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from models import Base


class FamAccessControlPrivilegeModel(Base):
    __tablename__ = "fam_access_control_privilege"
    __table_args__ = (
        ForeignKeyConstraint(
            ["role_id"],
            ["app_fam.fam_role.role_id"],
            name="reffam_access_control_privilege_role",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["app_fam.fam_user.user_id"],
            name="reffam_access_control_privilege_user",
        ),
        PrimaryKeyConstraint(
            "access_control_privilege_id", name="fam_access_control_privilege_pk"
        ),
        UniqueConstraint("user_id", "role_id", name="fam_access_control_usr_rle_uk"),
        Index("ix_app_fam_fam_access_control_privilege_role_id", "role_id"),
        Index("ix_app_fam_fam_access_control_privilege_user_id", "user_id"),
        {
            "comment": "Access Control Privilege is a cross-reference object that allows "
            "for the identification of who are the delegated "
            "administrators(User) for an Application for a particular role.",
            "schema": "app_fam",
        },
    )
    access_control_privilege_id = Column(
        BigInteger,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
        comment="Automatically generated key used to identify the uniqueness of a User administers the Application role.",
    )
    user_id = Column(
        BigInteger,
        comment="Unique ID to reference and identify the user within FAM system.",
    )
    role_id = Column(
        BigInteger,
        comment="Unique ID to reference and identify the application role within FAM system.",
    )
    create_user = Column(
        String(100), comment="The user or proxy account that created the record."
    )
    create_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created or last updated.",
    )
    role = relationship(
        "FamRole", back_populates="fam_access_control_privilege", lazy="joined"
    )
    user = relationship(
        "FamUser", back_populates="fam_access_control_privileges", lazy="joined"
    )

    def __repr__(self):
        return (
            f"FamAccessControlPrivilege(user_id={self.user_id}, role_id={self.role_id})"
        )
