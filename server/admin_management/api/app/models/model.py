import datetime

from sqlalchemy import (BigInteger, Column, ForeignKeyConstraint, Identity,
                        Index, Integer, PrimaryKeyConstraint, String,
                        UniqueConstraint, func, text)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class FamApplication(Base):
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
        "FamApplicationClient", back_populates="application"
    )
    fam_role = relationship("FamRole", back_populates="application")
    fam_application_admin = relationship(
        "FamApplicationAdmin", back_populates="application"
    )
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


class FamApplicationAdmin(Base):
    __tablename__ = "fam_application_admin"
    __table_args__ = (
        PrimaryKeyConstraint("application_admin_id", name="fam_app_admin_pk"),
        ForeignKeyConstraint(
            ["application_id"],
            ["app_fam.fam_application.application_id"],
            name="reffam_application_admin_application",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["app_fam.fam_user.user_id"],
            name="reffam_application_admin_user",
        ),
        UniqueConstraint("user_id", "application_id", name="fam_app_admin_usr_app_uk"),
        {
            "comment": "Application Admin is a cross-reference object that "
            + "allows for the identification of who are the "
            + "administrators(User) for an Application, as well as which "
            + " Applications the User can administer.",
            "schema": "app_fam",
        },
    )
    application_admin_id = Column(
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
        comment="Automatically generated key used to identify the "
        + "uniqueness of a User administers the Application.",
    )
    user_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Unique ID to reference and identify the user within FAM system.",
    )
    application_id = Column(
        BigInteger,
        comment="Unique ID to reference and identify the application within "
        + "FAM system.",
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
        comment="The user or proxy account that created or last updated the "
        + "record. ",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )
    application = relationship(
        "FamApplication", back_populates="fam_application_admin", lazy="joined"
    )
    user = relationship(
        "FamUser", back_populates="fam_application_admin", lazy="joined"
    )


class FamAccessControlPrivilege(Base):
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
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )
    role = relationship("FamRole", back_populates="fam_access_control_privilege", lazy="joined")
    user = relationship("FamUser", back_populates="fam_access_control_privilege", lazy="joined")

    def __repr__(self):
        return f"FamAccessControlPrivilege(user_id={self.user_id}, role_id={self.role_id})"


class FamForestClient(Base):
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
        default=datetime.datetime.utcnow,
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )

    fam_role = relationship("FamRole", back_populates="client_number")


class FamUserType(Base):
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
        default=datetime.datetime.utcnow,
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
        PrimaryKeyConstraint("user_type_code", name="fam_user_type_code_pk"),
        {
            "comment": "A user type is a code that is associated with "
            "the user to indicate its identity provider.",
            "schema": "app_fam",
        },
    )


class FamUser(Base):
    __tablename__ = "fam_user"

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
    user_type_code = Column(
        String(2),
        nullable=False,
        comment="Identifies which type of the user it belongs to; IDIR, BCeID etc.",
    )
    user_name = Column(String(100), nullable=False)
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
    user_guid = Column(String(32))
    business_guid = Column(String(32), comment='The business guid of the user if is a business bceid user.')
    cognito_user_id = Column(String(100))
    first_name = Column(String(50), comment='The first name of the user')
    last_name = Column(String(50), comment='The last name of the user.')
    email = Column(String(250), comment='The email of the user.')
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the record.",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )
    user_type_relation = relationship(
        "FamUserType", backref="user_relation", lazy="joined"
    )
    fam_application_admin = relationship("FamApplicationAdmin", back_populates="user")
    fam_access_control_privilege = relationship(
        "FamAccessControlPrivilege", back_populates="user"
    )

    __table_args__ = (
        PrimaryKeyConstraint("user_id", name="fam_usr_pk"),
        UniqueConstraint("user_type_code", "user_guid", name="fam_usr_uk"),
        ForeignKeyConstraint(
            [user_type_code],
            ["app_fam.fam_user_type_code.user_type_code"],
            name="reffam_user_type",
        ),
        {
            "comment": "A user is a person or system that can authenticate "
            "and then interact with an application.",
            "schema": "app_fam",
        },
    )

    def __str__(self):
        return f"FamUser({self.user_id}, {self.user_name}, {self.user_type_code})"


class FamApplicationClient(Base):
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
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        server_default=text("LOCALTIMESTAMP"),
        comment="The date and time the record was created.",
    )
    application = relationship(
        "FamApplication", back_populates="fam_application_client"
    )


class FamRoleType(Base):
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
        default=datetime.datetime.utcnow,
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


class FamRole(Base):
    __tablename__ = "fam_role"

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
    role_name = Column(String(100), nullable=False)
    role_purpose = Column(String(300), nullable=True)
    display_name = Column(String(100), nullable=True)
    application_id = Column(BigInteger, nullable=False, index=True)
    client_number_id = Column(
        BigInteger,
        nullable=True,
        index=True,
        comment="Sequentially assigned number to identify a ministry client.",
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
    parent_role_id = Column(
        BigInteger,
        nullable=True,
        index=True,
        comment="Automatically generated key used to identify the uniqueness "
        + "of a Role within the FAM Application",
    )
    update_user = Column(
        String(100),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(timezone=True, precision=6),
        onupdate=datetime.datetime.utcnow,
        comment="The date and time the record was created or last updated.",
    )
    role_type_code = Column(
        String(2),
        nullable=False,
        comment="Identifies if the role is an abstract or concrete role. "
        + "Users should only be assigned to roles where "
        + "role_type=concrete",
    )

    application: Mapped[FamApplication] = relationship("FamApplication", back_populates="fam_role")
    client_number = relationship(
        "FamForestClient", back_populates="fam_role", lazy="joined"
    )
    parent_role = relationship(
        "FamRole", remote_side=[role_id], back_populates="parent_role_reverse"
    )
    parent_role_reverse = relationship(
        "FamRole", remote_side=[parent_role_id], back_populates="parent_role"
    )
    role_type_relation = relationship("FamRoleType", backref="role_relation")
    fam_access_control_privilege = relationship(
        "FamAccessControlPrivilege", back_populates="role"
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["application_id"],
            ["app_fam.fam_application.application_id"],
            name="reffam_application22",
        ),
        ForeignKeyConstraint(
            ["client_number_id"],
            ["app_fam.fam_forest_client.client_number_id"],
            name="reffam_forest_client24",
        ),
        ForeignKeyConstraint(
            ["parent_role_id"], ["app_fam.fam_role.role_id"], name="reffam_role23"
        ),
        PrimaryKeyConstraint("role_id", name="fam_rle_pk"),
        UniqueConstraint("role_name", "application_id", name="fam_rlnm_app_uk"),
        ForeignKeyConstraint(
            [role_type_code],
            ["app_fam.fam_role_type.role_type_code"],
            name="reffam_role_type",
        ),
        {
            "comment": "A role is a qualifier that can be assigned to a user "
            "in order to identify a privilege within the context of an "
            "application.",
            "schema": "app_fam",
        },
    )


class FamAppEnvironment(Base):
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
