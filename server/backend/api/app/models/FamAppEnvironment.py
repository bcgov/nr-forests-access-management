import datetime

from sqlalchemy import (
    Column,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from api.app.models import Base


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
        default=datetime.datetime.now(datetime.UTC),
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
        onupdate=datetime.datetime.now(datetime.UTC),
        comment="The date and time the record was created or last updated.",
    )

    __table_args__ = (
        PrimaryKeyConstraint("app_environment", name="fam_app_environment_pk"),
        {
            "comment": "Used by the application to indicate its environment.",
            "schema": "app_fam",
        },
    )
