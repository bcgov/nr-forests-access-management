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
    func,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base


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
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated "
        + "the record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )

    fam_application_client = relationship(
        "FamApplicationClientModel", back_populates="application"
    )
    fam_role = relationship("FamRoleModel", back_populates="application")

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
        return f"FamApplicationModel({self.application_id}, {self.application_name}, {self.app_environment})"


class FamApplicationClientModel(Base):
    __tablename__ = "fam_application_client"
    __table_args__ = (
        UniqueConstraint("cognito_client_id", "application_id", name="cognito_app_uk"),
        ForeignKeyConstraint(
            ["application_id"],
            ["app_fam.fam_application.application_id"],
            name="reffam_application31",
        ),
        PrimaryKeyConstraint("application_client_id", name="fam_app_cli_pk"),
        {
            "comment": "FAM needs to know the OIDC client ID in order to match to an "
            "application. The relationship between OIDC client and application "
            "is many-to-one because sometimes there is more than one OIDC "
            "client for an application and it is convenient to be able to "
            "configure the authorization once (at the application level) and "
            "re-use it (at the OIDC level).",
            "schema": "app_fam",
        },
    )

    application_client_id = Column(
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
        + " of an OIDC as it corresponds to an identified client ",
    )
    cognito_client_id = Column(String(32), nullable=False)
    create_user = Column(
        String(100),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        server_default=text("LOCALTIMESTAMP"),
        comment="The date and time the record was created.",
    )
    application_id = Column(
        BigInteger,
        comment="Automatically generated key used to identify the uniqueness "
        + "of an Application registered under FAM",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the "
        + "record. ",
    )
    update_date = Column(
        # String(9), server_default=text("LOCALTIMESTAMP"), comment="ZIP code."
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        server_default=text("LOCALTIMESTAMP"),
        comment="The date and time the record was created.",
    )
    application = relationship(
        "FamApplicationModel", back_populates="fam_application_client"
    )


class FamAppEnvironmentModel(Base):
    __tablename__ = "fam_app_environment"

    app_environment = Column(
        String(4), nullable=False, comment="Application environment."
    )

    description = Column(
        String(100),
        nullable=True,
        comment="Description of what the app_environment represents.",
    )

    effective_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
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
        PrimaryKeyConstraint("app_environment", name="fam_app_environment_pk"),
        {
            "comment": "Used by the application to indicate its environment.",
            "schema": "app_fam",
        },
    )
