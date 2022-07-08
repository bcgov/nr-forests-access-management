# coding: utf-8
from sqlalchemy import Column, ForeignKey, Numeric, String, Integer, Table, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class FamApplicationClient(Base):
    __tablename__ = 'fam_application_client'

    application_client_id = Column(Integer, primary_key=True, autoincrement=True)
    cognito_client_id = Column(String(32), nullable=False)
    create_user = Column(String(30), nullable=False)
    create_date = Column(TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE"))
    update_user = Column(String(30), nullable=False)
    update_date = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_DATE"))


class FamForestClient(Base):
    __tablename__ = 'fam_forest_client'

    client_number_id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String(100), nullable=False)
    create_user = Column(String(30), nullable=False)
    create_date = Column(TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE"))
    update_user = Column(String(30), nullable=False)
    update_date = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_DATE"))


class FamUser(Base):
    __tablename__ = 'fam_user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_type = Column(String(1), nullable=False)
    cognito_user_id = Column(String(32))
    user_name = Column(String(100), nullable=False)
    user_guid = Column(String(32), nullable=False, unique=True)
    create_user = Column(String(30), nullable=False)
    create_date = Column(TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE"))
    update_user = Column(String(30), nullable=False)
    update_date = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_DATE"))


class FamApplication(Base):
    __tablename__ = 'fam_application'

    application_id = Column(Integer, primary_key=True, autoincrement=True)
    application_name = Column(String(100), nullable=False)
    applicationdescription = Column(String(200), nullable=False)
    application_client_id = Column(Integer, ForeignKey('fam_application_client.application_client_id'))
    create_user = Column(String(30), nullable=False)
    create_date = Column(TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE"))
    update_user = Column(String(30), nullable=False)
    update_date = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_DATE"))

    application_client = relationship('FamApplicationClient')
    groups = relationship('FamGroup', secondary='fam_application_group_xref')


class FamGroup(Base):
    __tablename__ = 'fam_group'

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    purpose = Column(String(200), nullable=False)
    parent_group_id = Column(ForeignKey('fam_group.group_id'))
    client_number_id = Column(ForeignKey('fam_forest_client.client_number_id'))
    create_user = Column(String(30), nullable=False)
    create_date = Column(TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE"))
    update_user = Column(String(30), nullable=False)
    update_date = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_DATE"))

    client_number = relationship('FamForestClient')
    parent_group = relationship('FamGroup', remote_side=[group_id])
    roles = relationship('FamRole', secondary='fam_group_role_xref')
    users = relationship('FamUser', secondary='fam_user_group_xref')


t_fam_application_group_xref = Table(
    'fam_application_group_xref', metadata,
    Column('group_id', Integer, ForeignKey('fam_group.group_id'), primary_key=True, nullable=False),
    Column('application_id', Integer, ForeignKey('fam_application.application_id'), primary_key=True, nullable=False)
)


class FamRole(Base):
    __tablename__ = 'fam_role'

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(100), nullable=False)
    role_purpose = Column(String(200), nullable=False)
    parent_role_id = Column(Integer, ForeignKey('fam_role.role_id'))
    application_id = Column(Integer, ForeignKey('fam_application.application_id'), nullable=False)
    client_number_id = Column(Integer, ForeignKey('fam_forest_client.client_number_id'))
    create_user = Column(String(30), nullable=False)
    create_date = Column(TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE"))
    update_user = Column(String(30), nullable=False)
    update_date = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_DATE"))

    application = relationship('FamApplication')
    client_number = relationship('FamForestClient')
    parent_role = relationship('FamRole', remote_side=[role_id])
    users = relationship('FamUser', secondary='fam_user_role_xref')


t_fam_user_group_xref = Table(
    'fam_user_group_xref', metadata,
    Column('user_id', ForeignKey('fam_user.user_id'), primary_key=True, nullable=False),
    Column('group_id', ForeignKey('fam_group.group_id'), primary_key=True, nullable=False)
)


t_fam_group_role_xref = Table(
    'fam_group_role_xref', metadata,
    Column('role_id', ForeignKey('fam_role.role_id'), primary_key=True, nullable=False),
    Column('group_id', ForeignKey('fam_group.group_id'), primary_key=True, nullable=False)
)


t_fam_user_role_xref = Table(
    'fam_user_role_xref', metadata,
    Column('user_id', ForeignKey('fam_user.user_id'), primary_key=True, nullable=False),
    Column('role_id', ForeignKey('fam_role.role_id'), primary_key=True, nullable=False)
)
