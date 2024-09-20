import logging
from http import HTTPStatus

import pytest
from api.app.constants import PrivilegeChangeTypeEnum, UserType
from api.app.crud.services.permission_audit_service import \
    PermissionAuditService
from api.app.models.model import FamPrivilegeChangeAudit, FamUser
from api.app.schemas.fam_application import FamApplicationSchema
from api.app.schemas.fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema
from api.app.schemas.fam_role_with_client import FamRoleWithClientSchema
from api.app.schemas.fam_user_info import FamUserInfoSchema
from api.app.schemas.fam_user_role_assignment_create_response import \
    FamUserRoleAssignmentCreateRes
from api.app.schemas.fam_user_type import FamUserTypeSchema
from api.app.schemas.requester import RequesterSchema
from sqlalchemy.orm import Session
from testspg.constants import (TEST_USER_GUID_IDIR, TEST_USER_NAME_IDIR,
                               USER_GUID_BCEID_LOAD_2_TEST,
                               USER_NAME_BCEID_LOAD_2_TEST)

LOGGER = logging.getLogger(__name__)

# sample end user permission granted response - role with no scope
sample_end_user_permission_granted_no_scope_details = FamUserRoleAssignmentCreateRes(
	**{'status_code': HTTPStatus.OK,
		'detail': FamApplicationUserRoleAssignmentGetSchema(
		user_role_xref_id=999, user_id=9, role_id=4,
		user=FamUserInfoSchema(user_name='enduser', first_name='first', last_name='last', email='a@b.com',
			user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description='BCEID')),
		role=FamRoleWithClientSchema(role_name='FOM_REVIEWER', role_type_code='C',
		application=FamApplicationSchema(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
		role_id=999, display_name='Reviewer', role_purpose='Provides the privilege to review all FOMs in the system', client_number=None, parent_role=None)),
		'error_message': None
	}
 )


@pytest.fixture(scope="function")
def get_requester(db_pg_session: Session, setup_new_user):
	requester_user: FamUser = setup_new_user(
		UserType.IDIR,
		TEST_USER_NAME_IDIR,
		TEST_USER_GUID_IDIR
	)
	requester = RequesterSchema.model_validate(
		requester_user.__dict__
	)
	return requester


def test_audit_history_end_user_role_no_scope(
		db_pg_session: Session,
		setup_new_user,
		get_requester,
		mocker):
	# setup performer and change_target_user
	performer = get_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		USER_NAME_BCEID_LOAD_2_TEST,
		USER_GUID_BCEID_LOAD_2_TEST
	)
	mock_user_permission_granted_list = [sample_end_user_permission_granted_no_scope_details]
	enduser_privliege_granted_details_fn_spy = mocker.spy(PermissionAuditService, 'to_enduser_privliege_granted_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')

	# test the service: granting end user role with no scope.
	paService = PermissionAuditService(db_pg_session)
	paService.store_user_permissions_granted_audit_history(performer, change_target_user, mock_user_permission_granted_list)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == sample_end_user_permission_granted_no_scope_details.detail \
			.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one_or_none()
	LOGGER.info(f"audit_record: {audit_record.__dict__}")
	assert audit_record is not None
	assert change_performer_user_details_fn_spy.call_count == 1
	assert enduser_privliege_granted_details_fn_spy.call_count == 1
	assert audit_record.privilege_change_type_code == PrivilegeChangeTypeEnum.GRANT
	assert audit_record.change_target_user_id == change_target_user.user_id
	__verify_change_performer_user(audit_record, performer)


def __verify_change_performer_user(audit_record: FamPrivilegeChangeAudit, performer: FamUser):
	change_performer_user_details = audit_record.change_performer_user_details
	assert change_performer_user_details["username"] == performer.user_name
	assert change_performer_user_details["first_name"] == performer.first_name
	assert change_performer_user_details["last_name"] == performer.last_name
	assert change_performer_user_details["email"] == performer.email


def __verify_end_user_privilege_details():
	pass