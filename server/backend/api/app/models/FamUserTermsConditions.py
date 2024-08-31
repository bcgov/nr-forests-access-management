import datetime

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
from api.app.models import Base


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
        default=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        default=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created or last updated.",
    )

    user = relationship("FamUserModel", back_populates="fam_user_terms_conditions")
