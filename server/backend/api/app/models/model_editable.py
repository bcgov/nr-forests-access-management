import model_donotedit as model
import datetime
from sqlalchemy import BigInteger, Column, Identity, Integer

from sqlalchemy.dialects.postgresql import TIMESTAMP


class FamApplication(model.FamApplication):
    # def __init__(self):
    #     model.FamApplication.__init__(self)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {
        'polymorphic_identity': 'fam_application'
    }

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
        comment="Automatically generated key used to identify the uniqueness " +
                "of an Application registered under FAM",
    )

    # @declared_attr
    # def property1(cls):
    #     return model.FamApplication.__table__.c.get('property1', Column(Integer))


class FamForestClient(model.FamForestClient):
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

class FamUser(model.FamUser):
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
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created.",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )


class FamApplicationClient(model.FamApplicationClient):
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
        comment="Automatically generated key used to identify the uniqueness " +
                " of an OIDC as it corresponds to an identified client ",
    )


class FamGroup(model.FamGroup):
    group_id = Column(
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
        autoincrement=True,
        primary_key=True,
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created.",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )

class FamRole(model.FamRole):
    role_id = Column(
        # Use '.with_variant' for sqlite as it does not recognize BigInteger
        # Ref: 	https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#allowing-autoincrement-behavior-sqlalchemy-types-other-than-integer-integer
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
                "of a Role within the FAM Application",
    )
