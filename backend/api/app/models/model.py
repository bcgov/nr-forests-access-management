from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKeyConstraint,
    Identity,
    Index,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class FamApplication(Base):
    __tablename__ = "fam_application"
    __table_args__ = (
        PrimaryKeyConstraint("application_id", name="fam_app_pk"),
        UniqueConstraint("application_name", name="fam_app_name_uk"),
        {
            "comment": "An application is a digital product that fulfills a specific user "
            "goal. It can be a front-end application, a back-end API, a "
            "combination of these, or something else entirely.",
            "schema": "app_fam",
        },
    )

    application_id = Column(
        BigInteger,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        comment="Automatically generated key used to identify the uniqueness of an Application registered under FAM",
    )
    application_name = Column(String(100), nullable=False)
    application_description = Column(String(200), nullable=False)
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    fam_application_client = relationship(
        "FamApplicationClient", back_populates="application"
    )
    fam_role = relationship("FamRole", back_populates="application")
    fam_application_group_xref = relationship(
        "FamApplicationGroupXref", back_populates="application"
    )


class FamForestClient(Base):
    __tablename__ = "fam_forest_client"
    __table_args__ = (
        PrimaryKeyConstraint("client_number_id", name="fam_for_cli_pk"),
        UniqueConstraint("client_name", name="fam_for_cli_name_uk"),
        {
            "comment": "A forest client is a business, individual, or agency that is "
            'identified as an entity that a user can have a privilege "on '
            'behalf of".',
            "schema": "app_fam",
        },
    )

    client_number_id = Column(
        BigInteger,
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
    client_name = Column(String(100), nullable=False)
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    fam_group = relationship("FamGroup", back_populates="client_number")
    fam_role = relationship("FamRole", back_populates="client_number")


class FamUser(Base):
    __tablename__ = "fam_user"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", name="fam_usr_pk"),
        UniqueConstraint("user_type", "user_name", name="fam_usr_uk"),
        {
            "comment": "A user is a person or system that can authenticate and then "
            "interact with an application.",
            "schema": "app_fam",
        },
    )

    user_id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        comment="Automatically generated key used to identify the uniqueness of a User within the FAM Application",
    )
    user_type = Column(String(1), nullable=False)
    user_name = Column(String(100), nullable=False)
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    user_guid = Column(String(32))
    cognito_user_id = Column(String(32))
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    fam_user_group_xref = relationship("FamUserGroupXref", back_populates="user")
    fam_user_role_xref = relationship("FamUserRoleXref", back_populates="user")


class FamApplicationClient(Base):
    __tablename__ = "fam_application_client"
    __table_args__ = (
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
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        comment="Automatically generated key used to identify the uniqueness of an OIDC as it corresponds to an identified client ",
    )
    cognito_client_id = Column(String(32), nullable=False)
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    application_id = Column(
        BigInteger,
        comment="Automatically generated key used to identify the uniqueness of an Application registered under FAM",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        String(9), server_default=text("CURRENT_DATE"), comment="ZIP code."
    )

    application = relationship(
        "FamApplication", back_populates="fam_application_client"
    )


class FamGroup(Base):
    __tablename__ = "fam_group"
    __table_args__ = (
        ForeignKeyConstraint(
            ["client_number_id"],
            ["app_fam.fam_forest_client.client_number_id"],
            name="reffam_forest_client25",
        ),
        ForeignKeyConstraint(
            ["parent_group_id"], ["app_fam.fam_group.group_id"], name="reffam_group16"
        ),
        PrimaryKeyConstraint("group_id", name="fam_grp_pk"),
        UniqueConstraint("group_name", name="fam_grp_name_uk"),
        {
            "comment": "A group is a collection of roles. When a group is assigned to a "
            "user, the user indirectly assumes the privileges of all the roles "
            "encompassed by the group. Groups are used to define profiles in "
            "order to make it easier to manage common sets of roles for users. "
            "A group can contain roles from multiple applications in order to "
            "handle the case where users typically have a certain set of "
            "privileges across multiple applications.",
            "schema": "app_fam",
        },
    )

    group_id = Column(
        BigInteger,
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
        primary_key=True
    )
    group_name = Column(String(100), nullable=False)
    purpose = Column(String(200), nullable=False)
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    parent_group_id = Column(BigInteger, index=True)
    client_number_id = Column(
        BigInteger,
        index=True,
        comment="Sequentially assigned number to identify a ministry client.",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    client_number = relationship("FamForestClient", back_populates="fam_group")
    parent_group = relationship(
        "FamGroup", remote_side=[group_id], back_populates="parent_group_reverse"
    )
    parent_group_reverse = relationship(
        "FamGroup", remote_side=[parent_group_id], back_populates="parent_group"
    )
    fam_application_group_xref = relationship(
        "FamApplicationGroupXref", back_populates="group"
    )
    fam_group_role_xref = relationship("FamGroupRoleXref", back_populates="group")
    fam_user_group_xref = relationship("FamUserGroupXref", back_populates="group")


class FamRole(Base):
    __tablename__ = "fam_role"
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
        UniqueConstraint("role_name", name="fam_rle_name_uk"),
        {
            "comment": "A role is a qualifier that can be assigned to a user in order to "
            "identify a privilege within the context of an application.",
            "schema": "app_fam",
        },
    )

    role_id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        comment="Automatically generated key used to identify the uniqueness of a Role within the FAM Application",
    )
    role_name = Column(String(100), nullable=False)
    role_purpose = Column(String(200), nullable=False)
    application_id = Column(BigInteger, nullable=False, index=True)
    client_number_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Sequentially assigned number to identify a ministry client.",
    )
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    parent_role_id = Column(
        BigInteger,
        index=True,
        comment="Automatically generated key used to identify the uniqueness of a Role within the FAM Application",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    application = relationship("FamApplication", back_populates="fam_role")
    client_number = relationship("FamForestClient", back_populates="fam_role")
    parent_role = relationship(
        "FamRole", remote_side=[role_id], back_populates="parent_role_reverse"
    )
    parent_role_reverse = relationship(
        "FamRole", remote_side=[parent_role_id], back_populates="parent_role"
    )
    fam_group_role_xref = relationship("FamGroupRoleXref", back_populates="role")
    fam_user_role_xref = relationship("FamUserRoleXref", back_populates="role")


class FamApplicationGroupXref(Base):
    __tablename__ = "fam_application_group_xref"
    __table_args__ = (
        ForeignKeyConstraint(
            ["application_id"],
            ["app_fam.fam_application.application_id"],
            name="reffam_application20",
        ),
        ForeignKeyConstraint(
            ["group_id"], ["app_fam.fam_group.group_id"], name="reffam_group19"
        ),
        PrimaryKeyConstraint("application_id", "group_id", name="fam_app_grp_xref"),
        {"schema": "app_fam"},
    )

    application_id = Column(BigInteger, nullable=False, index=True)
    group_id = Column(BigInteger, nullable=False, index=True)
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    application = relationship(
        "FamApplication", back_populates="fam_application_group_xref"
    )
    group = relationship("FamGroup", back_populates="fam_application_group_xref")


class FamGroupRoleXref(Base):
    __tablename__ = "fam_group_role_xref"
    __table_args__ = (
        ForeignKeyConstraint(
            ["group_id"], ["app_fam.fam_group.group_id"], name="reffam_group18"
        ),
        ForeignKeyConstraint(
            ["role_id"], ["app_fam.fam_role.role_id"], name="reffam_role17"
        ),
        PrimaryKeyConstraint("group_id", "role_id", name="fam_grp_rle_pk"),
        {"schema": "app_fam"},
    )

    group_id = Column(BigInteger, nullable=False, index=True)
    role_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Automatically generated key used to identify the uniqueness of a Role within the FAM Application",
    )
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    group = relationship("FamGroup", back_populates="fam_group_role_xref")
    role = relationship("FamRole", back_populates="fam_group_role_xref")


class FamUserGroupXref(Base):
    __tablename__ = "fam_user_group_xref"
    __table_args__ = (
        ForeignKeyConstraint(
            ["group_id"], ["app_fam.fam_group.group_id"], name="reffam_group30"
        ),
        ForeignKeyConstraint(
            ["user_id"], ["app_fam.fam_user.user_id"], name="reffam_user29"
        ),
        PrimaryKeyConstraint("user_id", "group_id", name="fam_usr_rle_pk_1"),
        {
            "comment": "User Group Xref is a cross-reference object that allows for the "
            "identification of Groups assigned to a user, as well as the users "
            "that belong to a given Group",
            "schema": "app_fam",
        },
    )

    user_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Automatically generated key used to identify the uniqueness of a User within the FAM Application",
    )
    group_id = Column(BigInteger, nullable=False, index=True)
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    group = relationship("FamGroup", back_populates="fam_user_group_xref")
    user = relationship("FamUser", back_populates="fam_user_group_xref")


class FamUserRoleXref(Base):
    __tablename__ = "fam_user_role_xref"
    __table_args__ = (
        ForeignKeyConstraint(
            ["role_id"], ["app_fam.fam_role.role_id"], name="reffam_role12"
        ),
        ForeignKeyConstraint(
            ["user_id"], ["app_fam.fam_user.user_id"], name="reffam_user10"
        ),
        PrimaryKeyConstraint("user_id", "role_id", name="fam_usr_rle_pk"),
        {
            "comment": "User Role Xref is a cross-reference object that allows for the "
            "identification of Roles assigned to a user, as well as the users "
            "that belong to a given Role",
            "schema": "app_fam",
        },
    )

    user_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Automatically generated key used to identify the uniqueness of a User within the FAM Application",
    )
    role_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Automatically generated key used to identify the uniqueness of a Role within the FAM Application",
    )
    create_user = Column(
        String(30),
        nullable=False,
        comment="The user or proxy account that created the record.",
    )
    create_date = Column(
        TIMESTAMP(precision=6),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created.",
    )
    update_user = Column(
        String(30),
        comment="The user or proxy account that created or last updated the record. ",
    )
    update_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_DATE"),
        comment="The date and time the record was created or last updated.",
    )

    role = relationship("FamRole", back_populates="fam_user_role_xref")
    user = relationship("FamUser", back_populates="fam_user_role_xref")
