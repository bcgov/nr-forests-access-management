import datetime

from sqlalchemy import (
    Column,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from api.app.models import Base


class FamRoleTypeModel(Base):
    __tablename__ = "fam_role_type"

    # ROLE_TYPE_ABSTRACT = 'A'
    # ROLE_TYPE_CONCRETE = 'C'

    role_type_code = Column(String(2), nullable=False, comment="role type code")

    description = Column(
        String(100),
        nullable=True,
        comment="Description of what the role_type_code represents",
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
        PrimaryKeyConstraint("role_type_code", name="fam_role_type_code_pk"),
        # CheckConstraint(role_type_code.in_(['C', 'A'])),
        {
            "comment": "A role type is a code that is associated with roles "
            "that will influence what can be associate with a role.  At time "
            "of implementation an abstract role can only have other roles "
            "related to it, while a concrete role can only have users "
            "associated with it",
            "schema": "app_fam",
        },
    )
