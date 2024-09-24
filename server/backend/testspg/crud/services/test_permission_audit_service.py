import copy
import logging
from http import HTTPStatus
from typing import List

import pytest
from api.app.constants import (ERROR_CODE_UNKNOWN_STATE,
                               PrivilegeChangeTypeEnum,
                               PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum, UserType)
from api.app.crud.services.permission_audit_service import \
    PermissionAuditService
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.models.model import (FamApplication, FamForestClient,
                                  FamPrivilegeChangeAudit, FamRole, FamUser,
                                  FamUserRoleXref)
from api.app.schemas.fam_application import FamApplicationSchema
from api.app.schemas.fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema
from api.app.schemas.fam_forest_client import FamForestClientSchema
from api.app.schemas.fam_role_min import FamRoleMinSchema
from api.app.schemas.fam_role_with_client import FamRoleWithClientSchema
from api.app.schemas.fam_user_info import FamUserInfoSchema
from api.app.schemas.fam_user_role_assignment_create_response import \
    FamUserRoleAssignmentCreateRes
from api.app.schemas.fam_user_type import FamUserTypeSchema
from api.app.schemas.requester import RequesterSchema
from fastapi import HTTPException
from mock import patch
from sqlalchemy.orm import Session
from testspg.constants import (FOM_DEV_APPLICATION_ID, TEST_USER_GUID_IDIR,
                               TEST_USER_NAME_IDIR,
                               USER_GUID_BCEID_LOAD_2_TEST,
                               USER_NAME_BCEID_LOAD_2_TEST)

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def new_idir_requester(db_pg_session: Session, setup_new_user):
	requester_user: FamUser = setup_new_user(
		UserType.IDIR,
		TEST_USER_NAME_IDIR,
		TEST_USER_GUID_IDIR
	)
	requester = RequesterSchema.model_validate(
		requester_user.__dict__
	)
	return requester


def test_store_end_user_audit_history_granted_role_no_scope(
	db_pg_session: Session,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving user permission granted history on role change with no scope.
	"""
	# setup performer and change_target_user
	performer = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		USER_NAME_BCEID_LOAD_2_TEST,
		USER_GUID_BCEID_LOAD_2_TEST
	)
	mock_user_permission_granted_list = [copy.copy(sample_end_user_permission_granted_no_scope_details)]
	enduser_privliege_granted_details_fn_spy = mocker.spy(PermissionAuditService, 'to_enduser_privliege_granted_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')

	# test the service: granting end user role with no scope.
	paService = PermissionAuditService(db_pg_session)
	paService.store_user_permissions_granted_audit_history(performer, change_target_user, mock_user_permission_granted_list)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_user_permission_granted_list[0].detail.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one()
	assert audit_record is not None
	assert change_performer_user_details_fn_spy.call_count == 1
	assert enduser_privliege_granted_details_fn_spy.call_count == 1
	assert audit_record.privilege_change_type_code == PrivilegeChangeTypeEnum.GRANT
	assert audit_record.change_target_user_id == change_target_user.user_id
	verify_change_performer_user(audit_record, performer)
	verify_end_user_granted_privilege_details(audit_record, mock_user_permission_granted_list)


def test_store_end_user_audit_history_granted_role_with_client_scopes(
	db_pg_session: Session,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving user permission granted history on role change with 'CLIENT' scopes.
	"""
	performer = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		USER_NAME_BCEID_LOAD_2_TEST,
		USER_GUID_BCEID_LOAD_2_TEST
	)
	mock_user_permission_granted_list = [copy.copy(sample_end_user_permission_granted_with_scope_details)]
	enduser_privliege_granted_details_fn_spy = mocker.spy(PermissionAuditService, 'to_enduser_privliege_granted_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')

	# test the service: granting end user role with scopes.
	paService = PermissionAuditService(db_pg_session)
	paService.store_user_permissions_granted_audit_history(performer, change_target_user, mock_user_permission_granted_list)

	# find the audit record and verify
	audit_records = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_user_permission_granted_list[0].detail.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).all()

	assert len(audit_records) == len(mock_user_permission_granted_list)
	assert change_performer_user_details_fn_spy.call_count == 1
	assert enduser_privliege_granted_details_fn_spy.call_count == 1
	for record in audit_records:
		assert record.privilege_change_type_code == PrivilegeChangeTypeEnum.GRANT
		assert record.change_target_user_id == change_target_user.user_id
		verify_change_performer_user(record, performer)
		verify_end_user_granted_privilege_details(record, mock_user_permission_granted_list)


def test_store_end_user_audit_history_revoke_role_no_scopes(
	db_pg_session: Session,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving user permission revoked history on role change with no scope.
	"""
	performer = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		USER_NAME_BCEID_LOAD_2_TEST,
		USER_GUID_BCEID_LOAD_2_TEST
	)
	mock_delete_record = copy.copy(sameple_user_role_with_no_client_revoked_record)
	mock_delete_record.user = change_target_user
	enduser_privliege_revoked_details_fn_spy = mocker.spy(PermissionAuditService, 'to_enduser_privliege_revoked_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')

	# test the service: granting end user role with scopes.
	paService = PermissionAuditService(db_pg_session)
	paService.store_user_permissions_revoked_audit_history(performer, mock_delete_record)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delete_record.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one()
	assert audit_record is not None
	assert enduser_privliege_revoked_details_fn_spy.call_count == 1
	assert change_performer_user_details_fn_spy.call_count == 1
	assert audit_record.privilege_change_type_code == PrivilegeChangeTypeEnum.REVOKE
	assert audit_record.change_target_user_id == change_target_user.user_id
	verify_change_performer_user(audit_record, performer)
	verify_end_user_revoked_privilege_details(audit_record, mock_delete_record)


@patch.object(ForestClientIntegrationService, "find_by_client_number")
def test_store_end_user_audit_history_revoke_role_with_client_scopes(
	mock_find_client_number,
	db_pg_session: Session,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving user permission revoked history on role change with 'CLIENT' scope.
	"""
	performer = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		USER_NAME_BCEID_LOAD_2_TEST,
		USER_GUID_BCEID_LOAD_2_TEST
	)
	mock_delete_record = copy.copy(sameple_user_role_with_client_revoked_record)
	mock_delete_record.user_id = change_target_user.user_id
	mock_delete_record.user = change_target_user
	mock_forest_client_number = "00001011"
	mock_delete_record.role.client_number.forest_client_number = mock_forest_client_number
	mock_delete_record.role.role_name = f"FOM_SUBMITTER_{mock_forest_client_number}"
	mock_find_client_number.return_value = MOCK_FIND_CLIENT_00001011_RETURN

	enduser_privliege_revoked_details_fn_spy = mocker.spy(PermissionAuditService, 'to_enduser_privliege_revoked_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')
	forest_client_integration_fn_spy = mocker.spy(ForestClientIntegrationService, 'find_by_client_number')

	# test the service: granting end user role with scopes.
	paService = PermissionAuditService(db_pg_session)
	paService.store_user_permissions_revoked_audit_history(performer, mock_delete_record)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delete_record.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one()
	assert audit_record is not None
	assert enduser_privliege_revoked_details_fn_spy.call_count == 1
	assert change_performer_user_details_fn_spy.call_count == 1
	assert forest_client_integration_fn_spy.call_count == 1
	assert audit_record.privilege_change_type_code == PrivilegeChangeTypeEnum.REVOKE
	assert audit_record.change_target_user_id == change_target_user.user_id
	verify_change_performer_user(audit_record, performer)
	verify_end_user_revoked_privilege_details(audit_record, mock_delete_record)


@patch.object(ForestClientIntegrationService, "find_by_client_number")
def test_store_end_user_audit_history_revoke_role_client_search_error(
	mock_find_client_number,
	db_pg_session: Session,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving user permission revoked history on role change with 'CLIENT' scope
	but with scenario that forest client number is not found (unknown reason) from
	FC integration external service. Exception should be raised and no audit record is saved.
	"""
	performer = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		USER_NAME_BCEID_LOAD_2_TEST,
		USER_GUID_BCEID_LOAD_2_TEST
	)
	mock_delete_record = copy.copy(sameple_user_role_with_notfound_client_revoked_record)
	mock_find_client_number.return_value = [] # FC external service result not found.
	forest_client_integration_fn_spy = mocker.spy(ForestClientIntegrationService, 'find_by_client_number')

	with pytest.raises(HTTPException) as e:
		paService = PermissionAuditService(db_pg_session)
		paService.store_user_permissions_revoked_audit_history(performer, mock_delete_record)

	assert str(e.value.detail.get("code")).find(ERROR_CODE_UNKNOWN_STATE) != -1
	error_msg = (
		"Revoke user permission encountered problem."
		+ f"Unknown forest client number {mock_delete_record.role.client_number.forest_client_number} for "
		+ f"scoped permission {mock_delete_record.role.role_name}."
	)
	assert (
		str(e.value.detail.get("description")).find(error_msg)
		!= -1
	)
	assert forest_client_integration_fn_spy.call_count == 1
	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delete_record.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one_or_none()
	assert audit_record is None


def verify_change_performer_user(audit_record: FamPrivilegeChangeAudit, performer: FamUser):
	audit_record.change_performer_user_id == performer.user_id
	change_performer_user_details_dict = audit_record.change_performer_user_details
	assert change_performer_user_details_dict["username"] == performer.user_name
	assert change_performer_user_details_dict["first_name"] == performer.first_name
	assert change_performer_user_details_dict["last_name"] == performer.last_name
	assert change_performer_user_details_dict["email"] == performer.email


def verify_end_user_granted_privilege_details(
	audit_record: FamPrivilegeChangeAudit,
	mock_user_permission_granted_list: List[FamUserRoleAssignmentCreateRes]
):
	audit_privilege_details_dict = audit_record.privilege_details
	assert audit_privilege_details_dict["permission_type"] == PrivilegeDetailsPermissionTypeEnum.END_USER
	assert len(audit_privilege_details_dict["roles"]) != 0
	audit_role = audit_privilege_details_dict["roles"][0] # FAM can grant 1 role at a time for now.
	granted_role = mock_user_permission_granted_list[0].detail.role
	assert audit_role["role"] == granted_role.display_name
	audit_scopes = audit_role.get("scopes")
	if granted_role.forest_client is None:
		# "scopes" attribute is not present if the granted role has no scopes.
		assert audit_scopes is None

	else:
		assert len(audit_scopes) == len(mock_user_permission_granted_list)
		org_id_list = list(map(
			lambda item: item.detail.role.forest_client.forest_client_number, mock_user_permission_granted_list
		))
		for scope in audit_scopes:
			scope.get("scope_type") == PrivilegeDetailsScopeTypeEnum.CLIENT  # Current FAM supports 'CLIENT' type only, more in future.
			scope.get("client_id") in org_id_list


def verify_end_user_revoked_privilege_details(
	audit_record: FamPrivilegeChangeAudit,
	mock_delete_record: FamUserRoleXref
):
	audit_privilege_details_dict = audit_record.privilege_details
	assert audit_privilege_details_dict["permission_type"] == PrivilegeDetailsPermissionTypeEnum.END_USER
	assert len(audit_privilege_details_dict["roles"]) != 0
	audit_role = audit_privilege_details_dict["roles"][0] # FAM can revoke 1 role at a time for now.
	revoked_role = mock_delete_record.role
	assert audit_role["role"] == revoked_role.display_name
	audit_scopes = audit_role.get("scopes")
	if not revoked_role.client_number_id:
		# "scopes" attribute is not present if the revoked role has no scopes.
		assert audit_scopes is None

	else:
		assert len(audit_scopes) == 1  # Fam can revoke role with 1 org at a time.
		org_id = revoked_role.client_number_id
		scope = audit_scopes[0]
		scope.get("scope_type") == PrivilegeDetailsScopeTypeEnum.CLIENT  # Current FAM supports 'CLIENT' type only, more in future.
		scope.get("client_id") == org_id


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

# sample end user permission granted response - role with forest_client scope
sample_end_user_permission_granted_with_scope_details = FamUserRoleAssignmentCreateRes(
	**{'status_code': HTTPStatus.OK,
		'detail': FamApplicationUserRoleAssignmentGetSchema(
		user_role_xref_id=888, user_id=9, role_id=127,
		user=FamUserInfoSchema(user_name='enduser', first_name='first', last_name='last', email='a@b.com',
			user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description='BCEID')),
		role=FamRoleWithClientSchema(role_name='FOM_SUBMITTER_00001012', role_type_code='C',
		application=FamApplicationSchema(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
		role_id=127, display_name='Submitter', role_purpose='Provides the privilege to submit a FOM (on behalf of a specific forest client)',
		client_number=FamForestClientSchema(client_name=None, forest_client_number="00001012", status=None),
		parent_role=FamRoleMinSchema(role_name="FOM_SUBMITTER", role_type_code="A",
			application=FamApplicationSchema(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)')))),
		'error_message': None
	}
 )

sameple_user_role_with_no_client_revoked_record = FamUserRoleXref(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(** {"display_name": "Reviewer", "application": FamApplication(** {"application_id": 2})})
})

sameple_user_role_with_client_revoked_record = FamUserRoleXref(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_00001011",
		"application": FamApplication(** {"application_id": FOM_DEV_APPLICATION_ID, }),
		"client_number_id": 3, "client_number": FamForestClient(**{
			"forest_client_number": "00001011"
		})
   })
})

sameple_user_role_with_notfound_client_revoked_record = FamUserRoleXref(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_09090909",
		"application": FamApplication(** {"application_id": FOM_DEV_APPLICATION_ID, }),
		"client_number_id": 3, "client_number": FamForestClient(**{
			"forest_client_number": "09090909"
		})
   })
})

MOCK_FIND_CLIENT_00001011_RETURN = [{
	'clientNumber': '00001011', 'clientName': 'AKIECA EXPLORERS LTD.', 'clientStatusCode': 'ACT', 'clientTypeCode': 'C'
}]
