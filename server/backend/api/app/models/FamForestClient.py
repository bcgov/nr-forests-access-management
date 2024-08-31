import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from api.app.models import Base


class FamForestClientModel(Base):
    __tablename__ = "fam_forest_client"
    __table_args__ = (
        PrimaryKeyConstraint("client_number_id", name="fam_for_cli_pk"),
        UniqueConstraint("forest_client_number", name="fam_for_cli_num_uk"),
        # UniqueConstraint("client_name", name="fam_for_cli_name_uk"),
        {
            "comment": "A forest client is a business, individual, or agency that is "
            'identified as an entity that a user can have a privilege "on '
            'behalf of".',
            "schema": "app_fam",
        },
    )

    client_number_id = Column(
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
        comment="Sequentially assigned number to identify a ministry client.",
    )
    forest_client_number = Column(
        String,
        nullable=False,
        index=True,
        comment="Id number as String from external Forest Client source(api/table) that identifies the Forest Client.",
    )
    # client_name = Column(String(100), nullable=True, index=True)  # noqa NOSONAR

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
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created or last updated.",
    )

    fam_role = relationship("FamRole", back_populates="client_number")
