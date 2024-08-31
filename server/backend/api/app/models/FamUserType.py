import datetime
from typing import List

from sqlalchemy import Column, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from api.app.models import Base


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
        default=datetime.datetime.now(datetime.UTC),
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
        PrimaryKeyConstraint("user_type_code", name="fam_user_type_code_pk"),
        {
            "comment": "A user type is a code that is associated with "
            "the user to indicate its identity provider.",
            "schema": "app_fam",
        },
    )
