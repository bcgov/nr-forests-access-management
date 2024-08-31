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
from models import Base


class FamApplicationModel(Base):
    __tablename__ = "fam_application"

    application_id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        comment="Automatically generated key used to identify the uniqueness "
        + "of an Application registered under FAM",
    )
    application_name = Column(String(100), nullable=False)
    application_description = Column(String(200), nullable=False)
    app_environment = Column(
        String(4),
        nullable=True,
        comment="Identifies which environment the application is for; DEV, TEST, PROD etc.",
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
        + "the record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created or last updated.",
    )

    fam_application_client = relationship(
        "FamApplicationClient", back_populates="application"
    )
    fam_role = relationship("FamRole", back_populates="application")

    __table_args__ = (
        PrimaryKeyConstraint("application_id", name="fam_app_pk"),
        UniqueConstraint("application_name", name="fam_app_name_uk"),
        ForeignKeyConstraint(
            [app_environment],
            ["app_fam.fam_app_environment.app_environment"],
            name="reffam_app_env",
        ),
        {
            "comment": "An application is a digital product that fulfills a  "
            "specific user goal. It can be a front-end application, a back-end "
            "API, a combination of these, or something else entirely.",
            "schema": "app_fam",
        },
    )

    def __repr__(self):
        return f"FamApplication({self.application_id}, {self.application_name}, {self.app_environment})"
