from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKeyConstraint,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base


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
